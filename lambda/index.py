import json
import os
import urllib.parse
import urllib.request

import boto3


# ============================================================
# CONFIGURATION
# ============================================================

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

REGION = "ap-south-1"


# ============================================================
# AWS CLIENTS
# ============================================================

ec2 = boto3.client("ec2", region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)
rds = boto3.client("rds", region_name=REGION)


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        result = response.read().decode("utf-8")

    print("Telegram response:", result)

    return result


# ============================================================
# EC2
# ============================================================

def get_ec2_instances():
    instances = []

    paginator = ec2.get_paginator("describe_instances")

    for page in paginator.paginate():

        for reservation in page["Reservations"]:

            for instance in reservation["Instances"]:

                state = instance["State"]["Name"]

                if state == "terminated":
                    continue

                instance_id = instance["InstanceId"]

                instance_type = instance["InstanceType"]

                public_ip = instance.get(
                    "PublicIpAddress",
                    "None"
                )

                name = "Unnamed"

                for tag in instance.get("Tags", []):

                    if tag["Key"] == "Name":
                        name = tag["Value"]

                instances.append({
                    "id": instance_id,
                    "name": name,
                    "type": instance_type,
                    "public_ip": public_ip,
                    "state": state
                })

    return instances


# ============================================================
# EBS
# ============================================================

def get_ebs_volumes():
    volumes = []

    paginator = ec2.get_paginator("describe_volumes")

    for page in paginator.paginate():

        for volume in page["Volumes"]:

            volumes.append({
                "id": volume["VolumeId"],
                "size": volume["Size"],
                "type": volume["VolumeType"],
                "state": volume["State"]
            })

    return volumes


# ============================================================
# ELASTIC IP / PUBLIC IPv4
# ============================================================

def get_elastic_ips():
    addresses = []

    response = ec2.describe_addresses()

    for address in response["Addresses"]:

        public_ip = address.get(
            "PublicIp",
            "Unknown"
        )

        allocation_id = address.get(
            "AllocationId",
            "Unknown"
        )

        association_id = address.get(
            "AssociationId"
        )

        if association_id:
            status = "Associated"
        else:
            status = "⚠️ Unassociated"

        addresses.append({
            "ip": public_ip,
            "allocation_id": allocation_id,
            "status": status
        })

    return addresses


# ============================================================
# NAT GATEWAYS
# ============================================================

def get_nat_gateways():
    gateways = []

    paginator = ec2.get_paginator("describe_nat_gateways")

    for page in paginator.paginate(
        Filters=[
            {
                "Name": "state",
                "Values": [
                    "pending",
                    "available"
                ]
            }
        ]
    ):

        for gateway in page["NatGateways"]:

            gateways.append({
                "id": gateway["NatGatewayId"],
                "state": gateway["State"]
            })

    return gateways


# ============================================================
# LOAD BALANCERS
# ============================================================

def get_load_balancers():
    load_balancers = []

    paginator = elbv2.get_paginator(
        "describe_load_balancers"
    )

    for page in paginator.paginate():

        for lb in page["LoadBalancers"]:

            load_balancers.append({
                "name": lb["LoadBalancerName"],
                "type": lb["Type"],
                "scheme": lb["Scheme"]
            })

    return load_balancers


# ============================================================
# RDS
# ============================================================

def get_rds():
    databases = []

    paginator = rds.get_paginator(
        "describe_db_instances"
    )

    for page in paginator.paginate():

        for db in page["DBInstances"]:

            databases.append({
                "identifier": db["DBInstanceIdentifier"],
                "class": db["DBInstanceClass"],
                "engine": db["Engine"],
                "status": db["DBInstanceStatus"]
            })

    return databases


# ============================================================
# /LIVE MESSAGE
# ============================================================

def build_live_message():

    ec2_instances = get_ec2_instances()

    ebs_volumes = get_ebs_volumes()

    elastic_ips = get_elastic_ips()

    nat_gateways = get_nat_gateways()

    load_balancers = get_load_balancers()

    databases = get_rds()

    lines = []

    lines.append("💰 LIVE AWS RESOURCES")
    lines.append("📍 Region: ap-south-1")
    lines.append("")

    total_resources = 0


    # --------------------------------------------------------
    # EC2
    # --------------------------------------------------------

    if ec2_instances:

        lines.append("🖥 EC2")

        for instance in ec2_instances:

            lines.append(
                f"  • {instance['name']}"
            )

            lines.append(
                f"    {instance['id']} | "
                f"{instance['type']} | "
                f"{instance['state']}"
            )

            lines.append(
                f"    Public IP: "
                f"{instance['public_ip']}"
            )

            total_resources += 1

        lines.append("")


    # --------------------------------------------------------
    # EBS
    # --------------------------------------------------------

    if ebs_volumes:

        lines.append("💾 EBS")

        for volume in ebs_volumes:

            lines.append(
                f"  • {volume['id']} | "
                f"{volume['size']} GB | "
                f"{volume['type']} | "
                f"{volume['state']}"
            )

            total_resources += 1

        lines.append("")


    # --------------------------------------------------------
    # ELASTIC IP
    # --------------------------------------------------------

    if elastic_ips:

        lines.append("🌐 ELASTIC IP / PUBLIC IPv4")

        for address in elastic_ips:

            lines.append(
                f"  • {address['ip']} | "
                f"{address['status']}"
            )

            total_resources += 1

        lines.append("")


    # --------------------------------------------------------
    # NAT GATEWAY
    # --------------------------------------------------------

    if nat_gateways:

        lines.append("🚪 NAT GATEWAY")

        for gateway in nat_gateways:

            lines.append(
                f"  • {gateway['id']} | "
                f"{gateway['state']}"
            )

            total_resources += 1

        lines.append("")


    # --------------------------------------------------------
    # LOAD BALANCER
    # --------------------------------------------------------

    if load_balancers:

        lines.append("⚖️ LOAD BALANCER")

        for lb in load_balancers:

            lines.append(
                f"  • {lb['name']} | "
                f"{lb['type']} | "
                f"{lb['scheme']}"
            )

            total_resources += 1

        lines.append("")


    # --------------------------------------------------------
    # RDS
    # --------------------------------------------------------

    if databases:

        lines.append("🗄 RDS")

        for db in databases:

            lines.append(
                f"  • {db['identifier']}"
            )

            lines.append(
                f"    {db['class']} | "
                f"{db['engine']} | "
                f"{db['status']}"
            )

            total_resources += 1

        lines.append("")


    # --------------------------------------------------------
    # EMPTY
    # --------------------------------------------------------

    if total_resources == 0:

        lines.append(
            "✅ No cost-relevant resources found."
        )

    else:

        lines.append(
            "━━━━━━━━━━━━━━━━━━━━"
        )

        lines.append(
            f"Total resources: {total_resources}"
        )


    return "\n".join(lines)


# ============================================================
# TELEGRAM WEBHOOK
# ============================================================

def handle_telegram_webhook(event):

    body = event.get("body")

    if not body:
        return {
            "statusCode": 200,
            "body": "OK"
        }

    try:

        if isinstance(body, str):
            telegram_update = json.loads(body)
        else:
            telegram_update = body

    except json.JSONDecodeError:

        print("Invalid Telegram JSON")

        return {
            "statusCode": 400,
            "body": "Invalid JSON"
        }


    print(
        "TELEGRAM UPDATE:",
        json.dumps(telegram_update)
    )


    message = telegram_update.get(
        "message",
        {}
    )

    text = message.get(
        "text",
        ""
    ).strip()


    chat = message.get(
        "chat",
        {}
    )

    incoming_chat_id = chat.get(
        "id"
    )


    print(
        "Telegram command:",
        text
    )

    print(
        "Telegram chat ID:",
        incoming_chat_id
    )


    # --------------------------------------------------------
    # /live
    # --------------------------------------------------------

    if text == "/live":

        result = build_live_message()

        send_telegram(result)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Live resources sent"
            })
        }


    # Ignore everything else

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Ignored"
        })
    }


# ============================================================
# AWS EVENTBRIDGE
# ============================================================

def handle_aws_event(event):

    detail = event.get(
        "detail",
        {}
    )

    event_name = detail.get(
        "eventName",
        "TEST"
    )

    event_source = detail.get(
        "eventSource",
        "test.amazonaws.com"
    )

    region = event.get(
        "region",
        REGION
    )


    user_identity = detail.get(
        "userIdentity",
        {}
    )

    user = (
        user_identity.get("userName")
        or user_identity.get("principalId")
        or user_identity.get("arn")
        or "Unknown"
    )


    # --------------------------------------------------------
    # CREATED
    # --------------------------------------------------------

    if (
        event_name.startswith("Create")
        or event_name.startswith("Run")
    ):

        action = "🟢 CREATED"


    # --------------------------------------------------------
    # DELETED
    # --------------------------------------------------------

    elif (
        event_name.startswith("Delete")
        or event_name.startswith("Terminate")
    ):

        action = "🔴 DELETED"


    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    else:

        action = "ℹ️ EVENT"


    service = event_source.replace(
        ".amazonaws.com",
        ""
    )


    notification = (
        f"{action}\n\n"
        f"Service: {service}\n"
        f"Action: {event_name}\n"
        f"Region: {region}\n"
        f"User: {user}"
    )


    send_telegram(notification)


    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Notification sent"
        })
    }


# ============================================================
# MAIN LAMBDA HANDLER
# ============================================================

def lambda_handler(event, context):

    print(
        "RAW EVENT:",
        json.dumps(event)
    )


    # --------------------------------------------------------
    # Telegram / API Gateway request
    # --------------------------------------------------------

    if (
        "requestContext" in event
        or "body" in event
    ):

        return handle_telegram_webhook(event)


    # --------------------------------------------------------
    # EventBridge AWS event
    # --------------------------------------------------------

    if "detail" in event:

        return handle_aws_event(event)


    # --------------------------------------------------------
    # Unknown event
    # --------------------------------------------------------

    print("Unknown event type")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Unknown event"
        })
    }