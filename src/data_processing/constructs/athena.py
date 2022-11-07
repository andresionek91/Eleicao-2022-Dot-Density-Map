from aws_cdk import aws_athena as athena
from aws_cdk import aws_s3 as s3
from constructs import Construct


class AthenaConstruct(Construct):
    """Construct"""

    def __init__(
        self,
        scope: Construct,
        id: str,
    ) -> None:
        super().__init__(scope, id)

        self.bucket = s3.Bucket(
            scope=self,
            id="ResultsBucket",
        )

        self.work_group = athena.CfnWorkGroup(
            scope=self,
            id="Workgroup",
            name="eleicoes_workgroup",
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
                        encryption_option="SSE_S3",
                    ),
                    output_location=f"s3://{self.bucket.bucket_name}/eleicoes_workgroup/results",
                )
            ),
        )
