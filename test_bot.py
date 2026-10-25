import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from storage import ConfigStore


class BotTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.assertIsNotNone(importlib.util.find_spec('bot'), 'bot.py ainda não implementado')
        from bot import BestoBot
        self.folder = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.store = ConfigStore(Path(self.folder.name) / 'settings.db')
        self.llm = SimpleNamespace(complete=AsyncMock(return_value='Olá!'), close=AsyncMock())
        self.bot = BestoBot(self.store, self.llm)

    async def asyncTearDown(self):
        if hasattr(self, 'bot'):
            await self.bot.close()
            self.folder.cleanup()

    def interaction(self, admin=True):
        channel = SimpleNamespace(send=AsyncMock(), id=55)
        return SimpleNamespace(
            guild_id=123, guild=SimpleNamespace(id=123), channel=channel,
            user=SimpleNamespace(guild_permissions=SimpleNamespace(manage_guild=admin)),
            response=SimpleNamespace(send_message=AsyncMock(), defer=AsyncMock(), is_done=lambda: False),
            followup=SimpleNamespace(send=AsyncMock()),
        )

    async def test_ask_uses_server_agent_and_tone(self):
        self.store.update(123, configured=True, agent='Professor', tone='formal')
        interaction = self.interaction()
        await self.bot.tree.get_command('ask').callback(interaction, 'Explique Python')
        self.assertEqual(self.llm.complete.call_args.args[1], [{'role': 'user', 'content': 'Explique Python'}])
        self.assertIn('Professor', self.llm.complete.call_args.args[2])
        self.assertIn('formal', self.llm.complete.call_args.args[2])
        self.assertEqual(interaction.followup.send.call_args.args[0], 'Olá!')

    async def test_ask_refuses_unconfigured_server(self):
        interaction = self.interaction()
        await self.bot.tree.get_command('ask').callback(interaction, 'Oi')
        self.llm.complete.assert_not_awaited()
        self.assertIn('/config', interaction.response.send_message.call_args.args[0])

    async def test_configuration_requires_permission(self):
        interaction = self.interaction(admin=False)
        await self.bot.tree.get_command('config').callback(interaction, 'openai', 'demo', 'Tutor')
        self.assertFalse(self.store.get(123)['configured'])
        self.assertIn('Gerenciar servidor', interaction.response.send_message.call_args.args[0])

    async def test_configuration_saves_and_introduces_bot(self):
        interaction = self.interaction()
        await self.bot.tree.get_command('config').callback(interaction, 'openai', 'demo', 'Tutor')
        self.assertEqual(self.store.get(123)['model'], 'demo')
        self.assertTrue(self.store.get(123)['configured'])
        self.assertIn('BestoFriendo', interaction.channel.send.call_args.args[0])
        self.assertIn('privacidade', interaction.channel.send.call_args.args[0].lower())

    async def test_invalid_provider_not_persisted(self):
        interaction = self.interaction()
        await self.bot.tree.get_command('config').callback(interaction, 'unknown', 'demo', None)
        self.assertFalse(self.store.get(123)['configured'])

    async def test_tone_permission_and_persistence(self):
        command = self.bot.tree.get_command('tone')
        await command.callback(self.interaction(False), 'grosseiro')
        self.assertNotEqual(self.store.get(123)['tone'], 'grosseiro')
        await command.callback(self.interaction(), 'bem-humorado')
        self.assertEqual(self.store.get(123)['tone'], 'bem-humorado')

    async def test_resume_requires_consent_and_admin(self):
        self.store.update(123, configured=True)
        for admin, consent in [(False, True), (True, False)]:
            interaction = self.interaction(admin)
            await self.bot.tree.get_command('resume').callback(interaction, consent)
            self.assertFalse(self.bot.jobs)
            self.llm.complete.assert_not_awaited()
            interaction.response.send_message.assert_awaited_once()

    async def test_join_posts_introduction(self):
        channel = SimpleNamespace(
            permissions_for=lambda _: SimpleNamespace(view_channel=True, send_messages=True), send=AsyncMock())
        guild = SimpleNamespace(system_channel=channel, text_channels=[channel], me=object())
        await self.bot.on_guild_join(guild)
        self.assertIn('/config', channel.send.call_args.args[0])
        self.assertIn('BestoFriendo', channel.send.call_args.args[0])

    async def test_resume_reads_every_message_before_command(self):
        import datetime
        self.store.update(123, configured=True)
        interaction = self.interaction()
        interaction.created_at = datetime.datetime.now(datetime.timezone.utc)
        interaction.guild.me = object()
        interaction.channel.permissions_for = lambda _: SimpleNamespace(
            view_channel=True, read_message_history=True, send_messages=True)
        calls = []
        async def history(**kwargs):
            calls.append(kwargs)
            for index in range(250):
                yield SimpleNamespace(content=f'Conversa {index}', author=SimpleNamespace(display_name='Pessoa', id=7),
                                      created_at=interaction.created_at, id=index)
        interaction.channel.history = history
        await self.bot.tree.get_command('resume').callback(interaction, True)
        import asyncio
        await asyncio.gather(*list(self.bot.jobs))
        self.assertIsNone(calls[0]['limit'])
        self.assertTrue(calls[0]['oldest_first'])
        self.assertEqual(calls[0]['before'], interaction.created_at)
        self.assertFalse(self.bot.busy)
        self.assertIn('250', interaction.channel.send.call_args_list[0].args[0])
        self.assertTrue(self.llm.complete.await_count)

    async def test_startup_synchronizes_commands(self):
        from unittest.mock import patch
        with patch.dict('os.environ', {'DISCORD_GUILD_ID': ''}), patch.object(self.bot.tree, 'sync', new=AsyncMock()) as sync:
            await self.bot.setup_hook()
            sync.assert_awaited_once_with()

    async def test_command_error_is_private_and_sanitized(self):
        from discord import app_commands
        interaction = self.interaction()
        await self.bot.on_command_error(interaction, app_commands.AppCommandError('SECRET_TOKEN'))
        text = interaction.response.send_message.call_args.args[0]
        self.assertNotIn('SECRET_TOKEN', text)
        self.assertTrue(interaction.response.send_message.call_args.kwargs['ephemeral'])

    async def test_llm_error_reports_safe_reason_in_log_and_discord(self):
        from llm import LLMError
        interaction = self.interaction()
        with self.assertLogs('bestofriendo', level='WARNING') as captured:
            await self.bot.on_command_error(interaction, LLMError('Falha no provedor (HTTP 503).'))
        text = interaction.response.send_message.call_args.args[0]
        self.assertIn('HTTP 503', text)
        self.assertIn('indisponível', text)
        self.assertIn('HTTP 503', '\n'.join(captured.output))
        self.assertTrue(interaction.response.send_message.call_args.kwargs['ephemeral'])

    async def test_missing_llm_credential_is_explained(self):
        from llm import LLMError
        interaction = self.interaction()
        await self.bot.on_command_error(interaction, LLMError('Credencial ausente: configure GEMINI_API_KEY.'))
        self.assertIn('GEMINI_API_KEY', interaction.response.send_message.call_args.args[0])

    async def test_cli_check_does_not_connect(self):
        from bot import main
        self.assertEqual(main(['--check']), 0)

    async def test_resume_refuses_missing_history_permission(self):
        self.store.update(123, configured=True)
        interaction = self.interaction()
        interaction.guild.me = object()
        interaction.channel.history = object()
        interaction.channel.permissions_for = lambda _: SimpleNamespace(
            view_channel=True, read_message_history=False, send_messages=True)
        await self.bot.tree.get_command('resume').callback(interaction, True)
        self.assertFalse(self.bot.jobs)
        self.assertIn('histórico', interaction.response.send_message.call_args.args[0])

    async def test_discord_command_payloads_are_valid(self):
        for command in self.bot.tree.get_commands():
            payload = command.to_dict(self.bot.tree)
            self.assertLessEqual(len(payload['description']), 100)
            self.assertTrue(payload['dm_permission'] is False)

    async def test_long_reply_preserved_without_mentions(self):
        send = AsyncMock()
        text = '@everyone ' + 'A' * 5000
        await self.bot.deliver(send, text)
        self.assertEqual(''.join(call.args[0] for call in send.call_args_list), text)
        for call in send.call_args_list:
            self.assertLessEqual(len(call.args[0]), 1900)
            self.assertEqual(call.kwargs['allowed_mentions'].to_dict()['parse'], [])

    async def test_six_commands_and_help_are_registered(self):
        commands = {command.name: command for command in self.bot.tree.get_commands()}
        self.assertEqual(set(commands), {'ask', 'model', 'config', 'tone', 'resume', 'help'})
        interaction = self.interaction()
        await commands['help'].callback(interaction)
        text = interaction.response.send_message.call_args.args[0]
        for name in commands:
            self.assertIn('/' + name, text)


if __name__ == '__main__':
    unittest.main()
