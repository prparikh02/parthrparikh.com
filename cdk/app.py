#!/usr/bin/env python3

from aws_cdk import core

from cdk.cdk_stack import PersonalWebsiteStack


app = core.App()

# Versioning: v{Major:1}{Minor:1}{Path:1} (since periods are not allowed)
PersonalWebsiteStack(app, 'PersonalWebsiteStack-v100')

app.synth()
