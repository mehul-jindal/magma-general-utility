root@731ad8c93c1d:/app/5GC_APIs/OUT_YAML/openapi/OUT_PROTOBUF/gen_protos# cat OpsSubscribers.py
#!/usr/bin/python3.9

import grpc
from dbsubscriber.Subscriberdb_pb2 import AccessAndMobilitySubscriptionData
from models.snssai_pb2 import Snssai
from models.nssai_pb2 import Nssai
from models.ambr_rm_pb2 import AmbrRm

def create_am1_msg(imsi: str, slice_type: int, slice_diff: str, ambr_dl: str,
                   ambr_ul: str, dnn_name: str):
    gpsis=[]
    gpsis.append("msisdn-"+imsi)
    gpsis.append("imsi-"+imsi)

    snssai=Snssai(sst=slice_type, sd=slice_diff)

    defaultSingleNssais=[]
    defaultSingleNssais.append(snssai)

    singleNssais=[]
    singleNssais.append(snssai)

    nssai=Nssai(defaultSingleNssais=defaultSingleNssais, singleNssais=singleNssais)
    subscribedUeAmbr=AmbrRm(uplink=ambr_ul, downlink=ambr_dl)

    subscribedDnnList=[dnn_name, "default"]
    return(
            AccessAndMobilitySubscriptionData(gpsis=gpsis, nssai=nssai,
                                      subscribedUeAmbr=subscribedUeAmbr,
                                      subscribedDnnList=subscribedDnnList)
            )


am1_msg=create_am1_msg("001011234567534", 1, "000001", "2000 Mbps", "1000 Mbps", "apn3")

print(am1_msg)
