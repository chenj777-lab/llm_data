import os
import sys
import json
import yaml
import argparse
import base64

from dragonfly.common_leaf_dsl import LeafFlow, OfflineRunner
from dragonfly.ext.mio.mio_api_mixin import MioApiMixin
from dragonfly.ext.kuiba.kuiba_api_mixin import KuibaApiMixin
from dragonfly.ext.offline.offline_api_mixin import OfflineApiMixin
from dragonfly.ext.gsu.gsu_api_mixin import GsuApiMixin

parser = argparse.ArgumentParser()
parser.add_argument('--run', dest="run", default=False, action='store_true')
parser.add_argument('--group_id', type=str, help='read group_id')
parser.add_argument('--begin_time_ms', type=str, default='2021-04-01 12:00:00', help='read begin_time_ms')
parser.add_argument('--end_time_ms', type=str, default='2021-04-01 13:00:00', help='read end_time_ms')
parser.add_argument('--parameter_config', type=str, default='../parameter_config.json', help='kuiba parameter configuration. as pipeline input.')
parser.add_argument('-s', '--src', type=str, default='hdfs-kafka', help='sample source: hdfs/kfaka/btq/local')
parser.add_argument('-o', '--output', type=str, default='./', help='directory of generated pipeline.json')
parser.add_argument('-f', '--force', dest="force", default=False, action='store_true', help='force overwrite existing pipeline.json')
parser.add_argument('-m', '--mode', type=str, default='train', help='train/eval')

args = parser.parse_args()

current_dir = os.path.dirname(__file__)

# load plugins
class DataReaderFlow(LeafFlow, MioApiMixin, KuibaApiMixin, OfflineApiMixin, GsuApiMixin):
  def clean_all(self, reason):
    return self.limit(0, name="clean_all_for_" + reason)

# define the pipeline
buyerhome_sample2mio_learner = DataReaderFlow(name = "buyerhome_sample2mio_learner")
if args.src == 'hdfs':
  if args.mode == 'train':
    print("using hdfs")
    buyerhome_sample2mio_learner = buyerhome_sample2mio_learner.fetch_message(
      group_id=args.group_id,
      hdfs_path="hdfs://lt-nameservice4.sy/home/reco/rawdata/eshop_vertical_page_sample/",
      #hdfs_path="hdfs://lt-nameservice4.sy/home/reco/rawdata/eshop_vertical_page_sample/%Y-%m-%d/%H/*",
      hdfs_read_thread_num=12,
      hdfs_timeout_ms=60 * 60 * 1000,
      begin_time_ms=args.begin_time_ms,
      end_time_ms=args.end_time_ms,
      hdfs_user_name="reco",
      #local_path="/media/disk1/fordata/mpi/yujinkai/merchant/eshop_hot_sample_small.txt",  # debug usage(1st priority)
      output_attr="raw_sample_package_str")
  else:
    buyerhome_sample2mio_learner = buyerhome_sample2mio_learner.fetch_message(
      hdfs_path="hdfs://lt-nameservice4.sy/home/reco/rawdata/eshop_vertical_page_sample/",
      #hdfs_path="hdfs://lt-nameservice4.sy/home/reco/rawdata/eshop_vertical_page_sample/%Y-%m-%d/%H/*",
      hdfs_read_thread_num=12,
      hdfs_timeout_ms=60 * 60 * 1000,
      output_attr="raw_sample_package_str")  
elif args.src == 'kafka':
  print("using kafka")
  buyerhome_sample2mio_learner = buyerhome_sample2mio_learner.fetch_message(
    group_id=args.group_id,
    kafka_topic="eshop_vertical_page_sample",
    begin_time_ms=args.begin_time_ms,
    output_attr="raw_sample_package_str")        
elif args.src == 'hdfs-kafka':
  print("first hdfs, then kafka")
  buyerhome_sample2mio_learner = buyerhome_sample2mio_learner.fetch_message(
    group_id=args.group_id,
    hdfs_path="hdfs://lt-nameservice4.sy/home/reco/rawdata/eshop_vertical_page_sample/",
    hdfs_read_thread_num=12,
    hdfs_timeout_ms=60 * 60 * 1000,
    begin_time_ms=args.begin_time_ms,
    kafka_topic="eshop_vertical_page_sample",
    hdfs_user_name="reco",
    output_attr="raw_sample_package_str")
else:
  print("using local data")
  buyerhome_sample2mio_learner = buyerhome_sample2mio_learner.fetch_message(
    local_path="/media/disk1/fordata/mpi/yujinkai/merchant/eshop_hot_sample_small.txt",
    output_attr="raw_sample_package_str")

buyerhome_sample2mio_learner = buyerhome_sample2mio_learner \
  .parse_protobuf_from_string(
    input_attr="raw_sample_package_str",
    output_attr="raw_sample_package",
    class_name="kuiba::RawSamplePackage") \
  .retrieve_from_raw_sample_package(
    skip_sample_without_labels=True,
    from_extra_var="raw_sample_package",
    labels=[
      dict(label="China,eshop_vertical_page,live_click", attr="click"),
      dict(label="China,eshop_vertical_page,live_watch_live_time", attr="wtime"),
      dict(label="China,eshop_vertical_page,live_realshow", attr="realshow"),
      dict(label="China,eshop_vertical_page,live_live_watch_item_buy", attr="live_watch_item_buy"),
      dict(label="China,eshop_vertical_page,live_live_view_interval_60s", attr="live_view_interval_60s"),
      dict(label="China,eshop_vertical_page,live_follow", attr="follow"),
    ],
    # debug usage
    #save_common_attr_names_to="common_attrs",
    #save_item_attr_names_to="item_attrs") \
  ) \

buyerhome_sample2mio_learner = buyerhome_sample2mio_learner \
  .copy_user_meta_info(save_result_size_to_attr="item_num") \
  .if_("item_num > 0") \
    .enrich_attr_by_lua(
      export_common_attr=["limit_num"],
      function_for_common="calculate",
      lua_script=f"""
        function calculate()
          return 50
        end
      """) \
    .colossus(
      service_name='grpc_colossusLiveItem',
      shard_number=16,
      client_type='common_item_client',
      output_attr='live_colossus_output') \
    .live_gsu_with_cluster(
      hetu_cluster_config_key_name='reco.model2.liveHetuEmbeddingIndex100',
      colossus_resp_attr='live_colossus_output',
      limit_num_attr='limit_num',
      output_sign_attr="live_gsu_signs",
      output_slot_attr="live_gsu_slots",
      slots_id=[1000, 1001, 1002, 1003, 1004],
      mio_slots_id=[1000, 1001, 1002, 1003, 1004],
      target_cluster_attr = 'lHetuCoverEmbeddingCluster',) \
  .end_if_()

buyerhome_sample2mio_learner = buyerhome_sample2mio_learner \
  .copy_user_meta_info(save_result_size_to_attr="item_num") \
  .if_("item_num > 0") \
    .extract_kuiba_parameter(
      slots_output="slots",
      parameters_output="signs",
      config=json.load(open(args.parameter_config))) \
    .send_to_mio_learner(
      attrs=["click", "wtime", "realshow", "live_watch_item_buy", "live_view_interval_60s", "follow",
          "bh_live_ctr", "bh_wtr", "bh_lvtr", "bh_cvr", "bh_wtime"],
      lineid_attr="_USER_ID_",
      user_hash_attr="_DEVICE_ID_",
      time_ms_attr="_REQ_TIME_",
      pid_attr="pId",
      label_attr="click",
      slots_attrs=["slots", "live_gsu_slots"],
      signs_attrs=["signs", "live_gsu_signs"]) \
  .end_if_()

runner = OfflineRunner("buyerhome_sample2mio_learner")

if args.run:
  runner.IGNORE_UNUSED_ATTR = ["common_attrs", "item_attrs", "slots", "signs","rLocale","rChannel"]
  runner.add_leaf_flows(leaf_flows=[buyerhome_sample2mio_learner])

  exe = runner.executor()
  for i in range(1):
    exe.reset()
    exe.run("buyerhome_sample2mio_learner")
    if len(exe.items) <= 0:
      print("item_num <= 0, skipped.")
      continue
    print("common_attrs: ", (exe["common_attrs"]))
    # TODO(yujinkai): fix UnicodeDecodeError here
    #for key in (exe["common_attrs"] or []):
    #  print(key, exe[key])

    print("item_keys: ", exe.item_keys)
    for item in exe.items:
      print("item_key: ", item.item_key)
      for key in (item["item_attrs"] or []) + ["click", "wtime", "realshow", "live_watch_item_buy", "live_view_interval_60s", "follow","slots", "signs"]:
        print(key, item[key])
    _ = input('press to continue consuming...')
else:
  runner.IGNORE_UNUSED_ATTR = ["common_attrs", "item_attrs", "slots", "signs","rLocale","rChannel"]
  runner.add_leaf_flows(leaf_flows = [buyerhome_sample2mio_learner])
  output_file_name = "cofea_reader_bk.json" #if args.mode == 'train' else "eval_pipeline.json"
  output_file = os.path.join(args.output, output_file_name)
  if os.path.exists(output_file) and (not args.force):
    print(f"{output_file} already exists, please check! exiting...")
    sys.exit(1)
  runner.build(output_file=output_file)
  if args.mode == 'train':
    print(f"Please set begin_time_ms and/or end_time_ms in {output_file} accordingly.")
  else:
    print(f"Please set begin_time and end_time in mio-learner.yaml accordingly.")

