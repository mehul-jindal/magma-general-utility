
#!/usr/bin/env python3

import argparse
import json
from google.protobuf import struct_pb2
from lte.protos.pmn_systems_pb2 import PMNSubscriberData
from lte.protos.models.any_type_pb2 import AnyType
from lte.protos.models.access_and_mobility_subscription_data_pb2 import AccessAndMobilitySubscriptionData
from lte.protos.models.authentication_subscription_pb2 import AuthenticationSubscription
from lte.protos.pmn_systems_pb2_grpc import PMNSubscriberConfigServicerStub
from lte.protos.pmn_systems_pb2 import SmfSelection
from lte.protos.pmn_systems_pb2 import SmDataPolicy
from lte.protos.pmn_systems_pb2 import SmData
from lte.protos.pmn_systems_pb2 import SmsData
from lte.protos.models.snssai_pb2 import Snssai
from lte.protos.models.nssai_pb2 import Nssai
from lte.protos.models.ambr_rm_pb2 import AmbrRm
from lte.protos.models.sequence_number_pb2 import SequenceNumber
from lte.protos.models.sign_pb2 import Sign
from lte.protos.models.smf_selection_subscription_data_pb2 import SmfSelectionSubscriptionData
from lte.protos.models.sms_management_subscription_data_pb2 import SmsManagementSubscriptionData
from lte.protos.models.ue_policy_set_pb2 import UePolicySet
from lte.protos.models.sms_subscription_data_pb2 import SmsSubscriptionData
from lte.protos.models.am_policy_data_pb2 import AmPolicyData
from lte.protos.models.session_management_subscription_data_pb2 import SessionManagementSubscriptionData
from lte.protos.models.smf_selection_subscription_data_pb2 import SmfSelectionSubscriptionData
from lte.protos.models.sm_policy_snssai_data_pb2 import SmPolicySnssaiData
from lte.protos.models.plmn_id_pb2 import PlmnId
from lte.protos.models.sm_policy_dnn_data_pb2 import SmPolicyDnnData
from lte.protos.models.dnn_info_pb2 import DnnInfo
from lte.protos.models.snssai_info_pb2 import SnssaiInfo
from lte.protos.models.ecgi_pb2 import Ecgi
from lte.protos.models.ncgi_pb2 import Ncgi
from lte.protos.models.tai_pb2 import Tai
from lte.protos.models.presence_info_pb2 import PresenceInfo
from lte.protos.models.dnn_configuration_pb2 import DnnConfiguration
from lte.protos.models.pdu_session_types_pb2 import PduSessionTypes
from lte.protos.models.ssc_modes_pb2 import SscModes
from lte.protos.models.subscribed_default_qos_pb2 import SubscribedDefaultQos
from lte.protos.models.arp_pb2 import Arp
from lte.protos.models.ambr_pb2 import Ambr
from lte.protos.models.plmn_route_selection_descriptor_pb2 import PlmnRouteSelectionDescriptor
from lte.protos.models.snssai_route_selection_descriptor_pb2 import SnssaiRouteSelectionDescriptor
from lte.protos.models.dnn_route_selection_descriptor_pb2 import DnnRouteSelectionDescriptor
from lte.protos.models.ue_policy_section_pb2 import UePolicySection
from lte.protos.models.operator_specific_data_pb2 import OperatorSpecificData
from lte.protos.models.subscriber_info_pb2 import QosProfileName
from lte.protos.models.service_subscription_pb2 import ServiceSubscriptionValue
from lte.protos.models.volume_accounting_pb2 import VolumeAccountingValue

def assemble_am1(args) -> AccessAndMobilitySubscriptionData:

    plmnAmData = struct_pb2.Struct()
    plmnAmData["{}-{}".format(args.mcc, args.mnc)]={}

    return AccessAndMobilitySubscriptionData(
              gpsis=["msisdn-{}".format(args.imsi)],
              nssai=Nssai(defaultSingleNssais=[Snssai(sst=args.st, sd=args.sd)],
                          #singleNssais=[Snssai(sst=args.st, sd=args.sd)]
                          ),
              subscribedUeAmbr=AmbrRm(uplink=args.subs_ambr_ul,
                                      downlink=args.subs_ambr_dl),
              subscribedDnnList=[args.dnn_name],
              plmnAmData=plmnAmData)

def assemble_smfSel(args) -> SmfSelection:
    dnnInfos = [DnnInfo(dnn="{}.mcc{}.mnc{}.gprs".format(args.dnn_name, args.mcc, args.mnc),
                        iwkEpsInd=True),
                DnnInfo(dnn="ims.mcc{}.mnc{}.gprs".format(args.mcc, args.mnc),
                        iwkEpsInd=True)]

    smfSelectionSubscriptionData=\
            SmfSelectionSubscriptionData(
            subscribedSnssaiInfos=({"{}-{}".format(args.st, args.sd):
                                   SnssaiInfo(dnnInfos=dnnInfos)}))

    return SmfSelection(plmnSmfSelData=\
            ({"{}-{}".format(args.mcc, args.mnc):smfSelectionSubscriptionData}))

def assemble_smData(args) -> SmData:
    #snssai=Snssai(sst=args.st,sd=args.sd)
    apn1_dnn_conf=DnnConfiguration(
          pduSessionTypes=PduSessionTypes(
            allowedSessionTypes=["IPV4V6"],
            defaultSessionType="IPV4"),
         internal_5gQosProfile=SubscribedDefaultQos(
            internal_5qi=9,
            arp=Arp(preemptCap="NOT_PREEMPT",preemptVuln="PREEMPTABLE",
                    priorityLevel=7)),
            sessionAmbr=Ambr(downlink="2 Mbps", uplink="1 Mbps"),
            sscModes=SscModes(
                     defaultSscMode="SSC_MODE_1",
                     allowedSscModes=["SSC_MODE_1","SSC_MODE_2","SSC_MODE_3"]))

    ims_dnn_conf=DnnConfiguration(
          pduSessionTypes=PduSessionTypes(
            allowedSessionTypes=["IPV4V6"],
            defaultSessionType="IPV4"),
         internal_5gQosProfile=SubscribedDefaultQos(
            internal_5qi=5,
            arp=Arp(preemptCap="NOT_PREEMPT",preemptVuln="PREEMPTABLE",
                    priorityLevel=7)),
            sessionAmbr=Ambr(downlink="2 Mbps", uplink="1 Mbps"),
            sscModes=SscModes(
                     defaultSscMode="SSC_MODE_1",
                     allowedSscModes=["SSC_MODE_1","SSC_MODE_2","SSC_MODE_3"]))

    sessionManagementSubscriptionData=\
            SessionManagementSubscriptionData(
                    singleNssai=Snssai(sst=args.st,sd=args.sd),
                    dnnConfigurations=({"apn1": apn1_dnn_conf,
                                        "ims": ims_dnn_conf}))

    listValue=struct_pb2.ListValue()
    from google.protobuf.json_format import MessageToJson
    listValue.extend([MessageToJson(sessionManagementSubscriptionData)])
    return SmData(plmnSmData=({"{}-{}".format(args.mcc, args.mnc): listValue}))


def assemble_auth_subs_data(args) -> AuthenticationSubscription:
    return AuthenticationSubscription(KTAB="AUTHSUBS", algorithmId="MILENAGE.1",
                                      authenticationManagementField="8000",
                                      authenticationMethod="5G_AKA",
                                      encOpcKey=args.opc,
                                      encPermanentKey=args.auth_key,
                                      protectionParameterId="none",
                                      sequenceNumber=\
                                       SequenceNumber(difSign="POSITIVE",
                                                      indLength=0,
                                                      sqnScheme="NON_TIME_BASED",
                                                      sqn="000000000000"))

def dump_subscriber_in_json(proto_msg):
    json_object = json.dumps(proto_msg, indent=1)
    print(json_object + ",")

def add_subscriber(client, args):

    am1 = assemble_am1(args)

    smfSel = assemble_smfSel(args)

    auth_subs_data = assemble_auth_subs_data(args)

    smData = assemble_smData(args)

    pmn_subs_data=\
        PMNSubscriberData(am1=am1, smfSel=smfSel,
                          auth_subs_data=auth_subs_data, smData=smData,)

    from google.protobuf.json_format import MessageToJson
    from google.protobuf.json_format import MessageToDict
    from google.protobuf.json_format import Parse
    #print(MessageToJson(pmn_subs_data))
    bevo_msg_dict={}

    bevo_msg_dict.update({"am1.json": MessageToDict(am1)})
    #dump_subscriber_in_json(am1_msg)

    bevo_msg_dict.update({"smfSel.json": MessageToDict(smfSel)})
    #dump_subscriber_in_json(smfSel_msg)

    bevo_msg_dict.update({"auth-subs-data.json": MessageToDict(auth_subs_data)})
    #dump_subscriber_in_json(auth_subs_data_msg)

    modified_smData = {"plmnSmData":{}}
    for key in smData.plmnSmData:
        sessionManagementSubscriptionData=[]
        for item in smData.plmnSmData[key]:
            res = json.loads(item)
            sessionManagementSubscriptionData.append(res)
        modified_smData["plmnSmData"][key]=sessionManagementSubscriptionData

    bevo_msg_dict.update({"sm-data.json": modified_smData})

    dump_subscriber_in_json(bevo_msg_dict)

    #client.PMNSubscriberConfig(pmn_subs_data)

def create_parser():
    """
    Creates the argparse parser with all the arguments.
    """
    parser = argparse.ArgumentParser(
        description='Management CLI for PMN Subscriber',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add subcommands
    subparsers = parser.add_subparsers(title="subcommands", dest="cmd")
    parser_add = subparsers.add_parser("add", help="Add a new subscriber")

    # Add arguments
    for cmd in [parser_add]:
        cmd.add_argument("--mcc", help="Mobile Country Code")
        cmd.add_argument("--mnc", help="Mobile Network Code")
        cmd.add_argument("--imsi", help="Subscriber ID")
        cmd.add_argument("--st", type=int, help="Slice type")
        cmd.add_argument("--sd", help="Slice differentiator")
        cmd.add_argument("--opc", help="encOpcKey")
        cmd.add_argument("--auth_key", help="encPermanentKey")
        cmd.add_argument("--subs_ambr_ul", help="Subscriber uplink Ambr")
        cmd.add_argument("--subs_ambr_dl", help="Subscriber downlink Ambr")
        cmd.add_argument("--dnn_name", help="Name of the dnn")
        cmd.add_argument("--dnn_ambr_ul", help="Dnn's uplink ambr")
        cmd.add_argument("--dnn_ambr_dl", help="Dnn's downlink ambr")
        cmd.add_argument("--qos_profile_5qi", help="Dnn's 5qi profile")


# Add function callbacks
    parser_add.set_defaults(func=add_subscriber)
    return parser

def main():
    parser = create_parser()

    # Parse the args
    args = parser.parse_args()
    if not args.cmd:
        parser.print_usage()
        exit(1)

    if args.cmd == 'add':
        if args.subs_ambr_dl is None or args.subs_ambr_ul is None or args.imsi is None\
                or args.sd is None or args.st is None or args.opc is None\
                or args.auth_key is None:
           parser.print_usage()
           exit(1)

    # Execute the subcommand function
    args.func(None, args)


if __name__ == "__main__":
    main()

#python3.9  strict_pmn_subscriber_cli.py add --mcc 724 --mnc 99 --imsi 724990000000008 --st 1 --sd "fff" --opc E8ED289DEBA952E4283B54E88E6183CA --auth_key 465B5CE8B199B49FAA5F0A2EE238A6BC --subs_ambr_ul "10 Mbps" --subs_ambr_dl "20 Mbps" --dnn_name "apn1" --dnn_ambr_ul "10 Mbps"   --dnn_ambr_dl "20 Mbps" --qos_profile_5qi 5
#python3.9  strict_pmn_subscriber_cli.py add --mcc 001 --mnc 01 --imsi 001011234567548 --st 1 --sd "000001" --opc E8ED289DEBA952E4283B54E88E6183CA --auth_key 465B5CE8B199B49FAA5F0A2EE238A6BC --subs_ambr_ul "10 Mbps" --subs_ambr_dl "20 Mbps" --dnn_name "apn1" --dnn_ambr_ul "10 Mbps"   --dnn_ambr_dl "20 Mbps" --qos_profile_5qi 5