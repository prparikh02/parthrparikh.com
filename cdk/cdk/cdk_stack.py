from aws_cdk import (
    core,
    aws_certificatemanager as acm,
    aws_cloudfront as cf,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    aws_iam as iam,
)

class PersonalWebsiteStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define S3 bucket that will host site assets
        website_bucket = s3.Bucket(
            self,
            'parthrparikh-com-assets-bucket',
            website_index_document='index.html',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
        # Deny non-SSL traffic
        website_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect=iam.Effect.DENY,
            actions=["s3:*"],
            resources=[website_bucket.bucket_arn],
            conditions={
                'Bool': {
                    'aws:SecureTransport': False,
                }
            },
            principals=[iam.AnyPrincipal()],
        ))
        s3_deploy.BucketDeployment(
            self,
            'parthrparikh-com-deploy-website',
            sources=[s3_deploy.Source.asset('../website/')],
            destination_bucket=website_bucket,
        )

        # Define certificate for parthrparikh.com
        cert = acm.Certificate(
            self,
            'parthrparikh-com-cert',
            domain_name='parthrparikh.com',
            subject_alternative_names=[
                'www.parthrparikh.com',
            ]
        )

        # Define CloudFront distribution
        origin_access_identity = cf.OriginAccessIdentity(
            self,
            'OriginAccessIdentity',
            comment='Personal website (parthrparikh.com) OAI to reach bucket',
        )
        website_bucket.grant_read(origin_access_identity)
        distro = cf.CloudFrontWebDistribution(
            self,
            'parthrparikh-com-distribution',
            origin_configs=[
                cf.SourceConfiguration(
                    s3_origin_source=cf.S3OriginConfig(
                        s3_bucket_source=website_bucket,
                        origin_access_identity=origin_access_identity
                    ),
                    behaviors=[
                        cf.Behavior(
                            is_default_behavior=True,
                            default_ttl=core.Duration.minutes(10),
                            max_ttl=core.Duration.hours(1),
                        )
                    ],
                ),
            ],
            viewer_certificate=cf.ViewerCertificate.from_acm_certificate(
                certificate=cert,
                aliases=[
                    'parthrparikh.com',
                    'www.parthrparikh.com',
                ]
            ),
            viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        )
