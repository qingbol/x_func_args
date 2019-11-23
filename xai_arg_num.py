'''
script for explain argument nums of function type 
'''
from rpy2 import robjects
from rpy2.robjects.packages import importr
import rpy2.robjects.numpy2ri
import os
import sys
import dataset
import converter
import eval_predict
import argparse
import configure
import cPickle as pickle
import numpy as np
np.random.seed(1234)
#np.set_printoptions(threshold = 1e6)
np.set_printoptions(threshold=sys.maxsize) 

r = robjects.r
rpy2.robjects.numpy2ri.activate()
importr('genlasso')
# importr('gsubfn')

class XaiFunction(object):
    def __init__(self,config_info):
        print "entering tst main"
        self.config_info = config_info
        self.data_folder = config_info['data_folder']
        self.func_path = config_info['func_path']
        self.embed_path = config_info['embed_path']
        self.tag = config_info['tag']
        data_tag = config_info['data_tag']
        self.process_num = int(config_info['process_num'])
        self.embed_dim = int(config_info['embed_dim'])
        # self.max_length = int(config_info['max_length'])
        self.num_classes = int(config_info['num_classes'])
        model_dir = config_info['model_dir']
        self.output_dir = config_info['output_dir']
        self.int2insn_path = config_info['int2insn_path']
        self.batch_size = config_info['batch_size']
        self.sample_num = int(config_info['sample_num'])

    def workfolow(self):
        with open(self.func_path) as f:
            func_info = pickle.load(f)
        # print "type of func_info:", type(func_info)
        # print "shape of func_info:", len(func_info)
        # print "data of func_info", func_info
        func_lst = func_info['train']
        # print "type of func_lst:", type(func_lst)
        print "shape of func_lst:", len(func_lst)
        # print "data of func_lst:", func_lst

        for index, func_name in enumerate(func_lst):
            self.func_name = func_name
            print "---------start of new function------------------------------"
            print "index in func_lst:", index
            print "func_name in func_lst:", self.func_name
            if index != 2 :
                continue
            # --------------start(read data )-----------------------------------
            func_lst_in_loop = []
            func_lst_in_loop.append(func_name)
            # print "type of  in func_lst_in_loop:", type(func_lst_in_loop)
            # print "data of  in func_lst_in_loop:", func_lst_in_loop
            data_batch = self.read_func_data(func_lst_in_loop)
            # print "************label of {}**********".format(self.func_name)
            # print "type of  in data_batch['label']:", type(data_batch['label'])
            print "data of  in data_batch['label']:", data_batch['label']
            # print "************label of {}**********".format(self.func_name)
            # -------------- end (read data )-----------------------------------

            # --------------start(convert data )--------------------------------
            embed_data_array, int_data_array, hex_data_array = \
                                            self.convert_insn2int(data_batch)
            # -------------- end (convert data )--------------------------------

            # --------------start(explain the prediction)-----------------------
            self.xai_function_type(embed_data_array, int_data_array, 
                                    hex_data_array)
            # -------------- end (explain the prediction)-----------------------

            print "--------- end of new function------------------------------"
        sys.exit(0)


    def read_func_data(self, func_lst_in_loop):
        # ------------start(retriev the target function data)------------------------
        function_data_file = func_lst_in_loop[0] + ".dat"
        function_data_path = os.path.join(self.output_dir, function_data_file)
        # result_path = os.path.join(self.output_dir, 'data_batch_result.pkl')
        if os.path.exists(function_data_path):
            with open(function_data_path, 'r') as f:
                data_batch = pickle.load(f)
            print('read the function data !!! ... %s' % function_data_path)
        else:
            my_data = dataset.Dataset(self.data_folder, func_lst_in_loop, 
                self.embed_path, self.process_num, self.embed_dim, 
                self.max_length, self.num_classes, self.tag, self.int2insn_path)
            data_batch = my_data.get_batch(batch_size = self.batch_size)
            with open(function_data_path, 'w') as f:
                pickle.dump(data_batch, f)
            print('Save the function_data_path !!! ... %s' % function_data_path)

        # *******start(used to predict the label of this data_batch)********
        # keep_prob = 1.0
        # feed_batch_dict1 = {
        #     'data': data_batch['data'],
        #     'label': data_batch['label'],
        #     'length': data_batch['length'],
        #     'keep_prob_pl': keep_prob
        # }
        # print "type of feed_batch_dict1['data']", type(feed_batch_dict1['data'])
        # print "len of feed_batch_dict1['data']", len(feed_batch_dict1['data'])
        # print "data of feed_batch_dict1['data']", feed_batch_dict1['data']
        # eval_predict.main(feed_batch_dict1)
        # ******* end (used to predict the label of this data_batch)********
        # ------------ end (retriev the target function data)------------------------
        return data_batch 


    def xai_function_type(self, embed_data_array, int_data_array, 
                        hex_data_array):
        # sample_num = 500
        # print "self.max_length", self.max_length
        tl = embed_data_array.shape[0]
        print "tl of embed_data_array.shape[0]", embed_data_array.shape[0]
        tc = embed_data_array.shape[1]
        print "tc of embed_data_array.shape[1]", embed_data_array.shape[1]
        half_tl = tl/2
        sample = np.random.randint(1, tl+1, self.sample_num)
        # print "sample len", len(sample)
        # print "sample shape: ", sample.shape
        # print "type of smaple", type(sample)

        features_range = range(tl)
        # features_range = range(tl+1)
        # print "feature_range type: ", type(features_range)
        # print "feature_range len", len(features_range)
        # print "feature_range data: ", features_range

        data_embed = np.copy(embed_data_array).reshape(1, tl, tc)
        data_int = np.copy(int_data_array).reshape(1, tl)
        # print "data of int_data_array", int_data_array
        # print "data of data_int", data_int
        for i, size in enumerate(sample, start=1):
            inactive = np.random.choice(features_range, size, replace=False)
            # print "type of inactive", type(inactive)
            # print 'inactive --->', inactive
            tmp_embed = np.copy(embed_data_array)
            tmp_embed[inactive] = 0
            tmp_embed = tmp_embed.reshape(1, tl, tc)
            data_embed = np.concatenate((data_embed, tmp_embed), axis=0)

            tmp_int = np.copy(int_data_array)
            tmp_int[inactive] = 0
            tmp_int = tmp_int.reshape(1, tl)
            data_int = np.concatenate((data_int, tmp_int), axis=0)
            # print "type of data_embed", type(data_embed)
            # print "shape of data_embed", data_embed.shape
        # print "type of data_embed", type(data_embed)
        # print "shape of data_embed", data_embed.shape
        # print "type of tmp_int", type(data_int)
        print "shape of tmp_int", data_int.shape

        # ---------start(prepare the dict which feed to eval)------------------------
        data_length = np.empty(self.sample_num + 1)
        data_length.fill(tl)
        # print "type of data_length", type(data_length)
        # print "len of data_length", len(data_length)
        # print "shape of data_length", data_length.shape
        # print "data of data_length", data_length
        data_label = np.empty([self.sample_num + 1, 16])
        data_label.fill(0)
        # print "type of data_label", type(data_label)
        # print "len of data_label", len(data_label)
        # print "shape of data_label", data_label.shape
        # print "data of data_label", data_label
        keep_prob = 1.0
        feed_batch_dict2 = {
            'data': data_embed,
            'label': data_label,
            'length': data_length,
            'keep_prob_pl': np.asarray(keep_prob, dtype=np.float32)
        }
        # print "type of feed_dict2[data_pl]", type(feed_batch_dict2['data'][0])
        # print "len of feed_dict2[data_pl]", len(feed_batch_dict2['data'][0])
        # print "data of feed_dict2[data_pl]", feed_batch_dict2['data'][0]
        # --------- end (prepare the dict which feed to eval)------------------------


        # ---------start(predict the label of 500 data)-----------------------------
        # print "func_name in func_lst:", self.func_name

        total_result = eval_predict.predict_main(feed_batch_dict2, 
                self.config_info, self.func_name, self.max_length)

        # print "type in total_result['pred']", type(total_result)
        print "shape in total_result['pred']", total_result.shape
        print "label in total_result['pred']", total_result
        label_sampled = total_result.reshape(self.sample_num + 1, 1)
        # print "type in label_sampled: ", type(label_sampled)
        # print "shape in label_sampled: ", label_sampled.shape
        # print "data  in label_sampled:", label_sampled

        #**********convert the value in label to 1 or 0 **************
        # label_sampled[label_sampled != 4] = 0
        # print "data  in total_result['pred']", label_sampled
        # label_sampled[label_sampled == 4] = 1
        # print "data  in total_result['pred']", label_sampled
        # --------- end (predict the label of 500 data)-----------------------------


        # ---------start(prepare the input data for regression model)---------------
        X = r.matrix(data_embed, nrow = data_embed.shape[0], 
                    ncol = data_embed.shape[1])
        # X = r.matrix(data_int, nrow = data_int.shape[0], ncol = data_int.shape[1])
        # print "type of X", type(X)
        # print "X data: ", X
        Y = r.matrix(label_sampled, nrow = label_sampled.shape[0], 
                    ncol = label_sampled.shape[1])
        # print "type of Y", type(Y)
        # print "Y data: ", Y

        n = r.nrow(X)
        p = r.ncol(X)
        results = r.fusedlasso1d(y=Y,X=X)
        # print "type of results: {}|row: {}|col: {}".format(
        #         type(results),r.nrow(results),r.ncol(results))
        result_original = np.array(r.coef(results, np.sqrt(n*np.log(p)))[0])
        # print "type of result_original: ", type(result_original)
        print "shape of result_original: ", result_original.shape
        result = np.array(r.coef(results, np.sqrt(n*np.log(p)))[0])[:,-1]
        # print "type of result: ", type(result)
        print "shape of result: ", result.shape
        # result_round=np.around(result, decimals=1)
        # print "data of result:{res:.2e} ".format(res=result)
        print "data of result: ",np.array_str(result, precision=2)
        significant_index = np.argsort(result)[::-1]
        print "data of significant_index: ", significant_index
        fea = np.zeros_like(hex_data_array) 
        # print "shape of fea", fea.shape
        # print "data of hex_data_array", hex_data_array
        fea[significant_index[0:7]] = hex_data_array[significant_index[0:7]]
        print "data of feature", fea.tolist()
        
        # --------- end (prepare the input data for regression model)---------------

    def convert_insn2int(self, data_batch):
        # ------------start(convert insn2int )---------------------------------------
        # original embedding data
        # print "type of data_batch['data']", type(data_batch['data'][0])
        # print "shape of data_batch['data']", len(data_batch['data'][0])
        # print "data of data_batch['data']", data_batch['data'][0]
        embed_data_array = data_batch['data'][0]
        # print "type of embed_data_array", type(embed_data_array)
        # print "data of embed_data_array", embed_data_array
        # embed_data_array[0].fill(0)
        # print "data of embed_data_array", embed_data_array

        # original hex data
        # print "type of data_batch['inst_types']", type(data_batch['inst_bytes'][0])
        print "shape of data_batch['inst_types']", len(data_batch['inst_bytes'][0])
        print "data of data_batch['inst_types']", data_batch['inst_bytes'][0]
        hex_data_list = data_batch['inst_bytes'][0]
        # print "type of hex_data_list", type(hex_data_list)
        # print "data of hex_data_list", hex_data_list
        hex_data_array = np.asarray(hex_data_list)
        # hex_data_array = np.array(hex_data_list)
        # hex_data_array = np.array([np.array(x) for x in hex_data_list])
        # print "data of hex_data_array", hex_data_array

        # int of hex data
        int2insn_map, int_data_list = converter.main(hex_data_list)
        print "type of int_data_list:", type(int_data_list)
        print "int data of int_data_list:", int_data_list
        # print "type of int2insn_map:", type(int2insn_map)
        # print "data of int2insn_map:", int2insn_map
        int_data_array = np.asarray(int_data_list)
        # print "type of int_data_array:", type(int_data_array)
        # print "shape of int_data_array:", int_data_array.shape
        # print "data of int_data_array", int_data_array

        # bin_data_list = [int2insn_map[k]
        #                  for k in int_data_list if k in int2insn_map]
        # bin_data_list = [int2insn_map[int(k)] for k in int_data_list if int(k) in int2insn_map]
        # print "type of bin_data_list", type(bin_data_list)
        # print "len of bin_data_list", len(bin_data_list)
        # print "data of bin_data_list", bin_data_list

        #**********get mat_length*********************
        self.max_length = int(data_batch['length'])
        # print "data of max_length:", self.max_length

        # ------------ end (convert insn2int )---------------------------------------
        return embed_data_array, int_data_array, hex_data_array


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ml', '--max_length', dest='max_length',
                        help='The maximun length of input sequences.', type=int, required=False, default=40)
    # parser.add_argument('-ml', '--max_length', dest='max_length', help='The maximun length of input sequences.', type=int, required=False, default=500)
    parser.add_argument('-i', '--int2insn_map_path', dest='int2insn_path', help='The pickle file saving int -> instruction mapping.',
                        type=str, required=False, default='/Users/tarus/TarusHome/10SrcFldr/CpSc8580EKLAVYA_py27/code/embedding/int2insn.map')
    # parser.add_argument('-i', '--int2insn_map_path', dest='int2insn_path', help='The pickle file saving int -> instruction mapping.', type=str, required=True)
    parser.add_argument('-d', '--data_folder', dest='data_folder', help='The data folder of testing dataset.',
                        type=str, required=False, default='/Users/tarus/OnlyInMac/dataset/eklavya/clean_pickles/x64')
    # parser.add_argument('-d', '--data_folder', dest='data_folder', help='The data folder of testing dataset.', type=str, required=True)
    parser.add_argument('-f', '--split_func_path', dest='func_path', help='The path of file saving the training & testing function names.',
                        type=str, required=False, default='/Users/tarus/TarusHome/10SrcFldr/CpSc8580EKLAVYA_py27/code/embedding/func_list/func_dict_x64_len40_gcc.lst')
    # parser.add_argument('-f', '--split_func_path', dest='func_path', help='The path of file saving the training & testing function names.', type=str, required=True)
    parser.add_argument('-e', '--embed_path', dest='embed_path', help='The path of file saving embedding vectors.',
                        type=str, required=False, default='/Users/tarus/OnlyInMac/dataset/eklavya/embed.pkl')
    # parser.add_argument('-e', '--embed_path', dest='embed_path', help='The path of file saving embedding vectors.', type=str, required=True)
    parser.add_argument('-m', '--model_dir', dest='model_dir', help='The directory saved the models.',
                        type=str, required=False, default='/Users/tarus/OnlyInMac/dataset/eklavya/rnn_output/model')
    # parser.add_argument('-m', '--model_dir', dest='model_dir', help='The directory saved the models.', type=str, required=True)

    parser.add_argument('-o', '--output_dir', dest='output_dir',
                        help='The directory to saved the evaluation result.', type=str, required=False, default='eval_output')
    # parser.add_argument('-o', '--output_dir', dest='output_dir', help='The directory to saved the evaluation result.', type=str, required=True)
    parser.add_argument('-t', '--label_tag', dest='tag',
                        help='The type of labels. Possible value: num_args, type#0, type#1, ...', type=str, required=False, default='num_args')
    parser.add_argument('-dt', '--data_tag', dest='data_tag', help='The type of input data.',
                        type=str, required=False, choices=['caller', 'callee'], default='callee')
    parser.add_argument('-pn', '--process_num', dest='process_num',
                        help='Number of processes.', type=int, required=False, default=4)
    parser.add_argument('-ed', '--embedding_dim', dest='embed_dim',
                        help='The dimension of embedding vector.', type=int, required=False, default=256)
    # parser.add_argument('-ml', '--max_length', dest='max_length', help='The maximun length of input sequences.', type=int, required=False, default=10)
    parser.add_argument('-nc', '--num_classes', dest='num_classes',
                        help='The number of classes', type=int, required=False, default=16)
    parser.add_argument('-do', '--dropout', dest='dropout',
                        help='The dropout value.', type=float, required=False, default=1.0)
    parser.add_argument('-nl', '--num_layers', dest='num_layers',
                        help='Number of layers in RNN.', type=int, required=False, default=3)
    parser.add_argument('-b', '--batch_size', dest='batch_size',
                        help='The size of batch.', type=int, required=False, default=1)

    args = parser.parse_args()
    config_info = {
        'data_folder': args.data_folder,
        'func_path': args.func_path,
        'embed_path': args.embed_path,
        'tag': args.tag,
        'data_tag': args.data_tag,
        'process_num': args.process_num,
        'embed_dim': args.embed_dim,
        'max_length': args.max_length,
        'num_classes': args.num_classes,
        'output_dir': args.output_dir,
        'model_dir': args.model_dir,
        'dropout': args.dropout,
        'num_layers': args.num_layers,
        'batch_size': args.batch_size,
        'int2insn_path': args.int2insn_path
    }
    return config_info


def main():
    config_info = configure.get_config()
    xai_func = XaiFunction(config_info)
    xai_func.workfolow()

if __name__ == '__main__':
    main()



def prepare_data_deprecated():
    # --------------start(read data from eval result)----------------------------
    # eval.main()

    # total_result['cost'].append(cost_result)
    # total_result['pred'].append(pred_result)
    # total_result['func_name'].append(func_name_list)
    # total_result['data'].append(data_list)
    print "config_info['input_data']", input_data
    result_file = open(config_info['input_data'])
    total_result = pickle.load(result_file)
    result_file.close()

    # hex of binary data
    print "type of total_result['data']", type(total_result['data'][0][0][:])
    print "shape of total_result['data']", total_result['data'][0][0][:].shape
    embed_data_list = total_result['data'][0][0][:]
    print "len of total_result['data']", len(embed_data_list)
    print "hex_data_list", embed_data_list[:]

    # original embedding data
    print "type of total_result['inst_types']", type(
        total_result['inst_bytes'][0][0][:])
    print "shape of total_result['inst_types']", len(
        total_result['inst_bytes'][0][0][:])
    print "data of total_result['inst_types']", total_result['inst_bytes'][0][0][:]
    hex_data_list = total_result['inst_bytes'][0][0]
    print "type of embed_data_list", type(hex_data_list)
    print "embedding data of embed_data_list", hex_data_list

    # int of embedding data
    int2insn_map, int_data_list = converter.main(hex_data_list)
    print "type of int_data_list", type(int_data_list)
    print "int data of int_data_list", int_data_list
    print "type of int2insn_map", type(int2insn_map)
    print "data of int2insn_map", int2insn_map
    bin_data_list = [int2insn_map[k]
                     for k in int_data_list if k in int2insn_map]
    # bin_data_list = [int2insn_map[int(k)] for k in int_data_list if int(k) in int2insn_map]
    print "type of bin_data_list", type(bin_data_list)
    print "len of bin_data_list", len(bin_data_list)
    print "data of bin_data_list", bin_data_list

    new_batch_data = {
        'data': [],
        'label': [],
        'length': [],
        # 'func_name':[],
        # 'inst_bytes':[]
    }
    new_batch_data['data'].append(embed_data_list)
    new_batch_data['length'].append(len(embed_data_list))
    # prepare_data()
    # data_pl, label_pl, length_pl, keep_prob_pl = eval_predict.placeholder_inputs(num_classes, max_length, embed_dim)
    keep_prob = 1.0
    feed_batch_dict = {
        'data': np.asarray(new_batch_data['data'], dtype=np.float32),
        'label': np.asarray(new_batch_data['label'], dtype=np.float32),
        'length': np.asarray(new_batch_data['length'], dtype=np.uint16),
        'keep_prob_pl': np.asarray(keep_prob, dtype=np.float32)
    }
    print "type of feed_dict[data_pl]", type(feed_batch_dict['data'][0])
    print "len of feed_dict[data_pl]", len(feed_batch_dict['data'][0])
    print "data of feed_dict[data_pl]", feed_batch_dict['data'][0]
    # -------------- end (read data from eval result)----------------------------

    # eval_predict.predict()
    eval_predict.main(feed_batch_dict)