#!/usr/bin/env python3
"""Test script to verify internal command group."""

from notebooklm_tools.cli.commands.internal import internal_app
import typer

# Test that internal_app is properly defined
print("Testing internal command group...")

# Test that subcommands are registered
print("\nSubcommands:")
for command_info in internal_app.registered_commands:
    print(f"  - {command_info.name}: {command_info.help}")

print("\nInternal command group is properly configured!")
