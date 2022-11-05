import pytest


@pytest.mark.parametrize(
    "type,count",
    [
        ("AWS::S3::Bucket", 0),
    ],
)
def test_resource_count(type, count, template_fixture):
    template_fixture.resource_count_is(type=type, count=count)


# def test_appsync_firewall_arn_parameter(template_fixture):
#     template_fixture.has_resource_properties(
#         type="AWS::S3::Bucket",
#         props={

#         },
#     )
