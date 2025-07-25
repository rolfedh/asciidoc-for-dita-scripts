#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.getcwd())

from asciidoc_dita_toolkit.plugins.vale_flagger.vale_flagger import ValeFlagger

vf = ValeFlagger()
config = vf._build_vale_config()
print("Generated Vale config:")
print("=" * 40)
print(config)
print("=" * 40)
