import numpy as np

#Rohit Gore
class RTLearner(object):
    def __init__(self,leaf_size,verbose=False):
        self.leaf_size=leaf_size
        self.learner = []
        self.verbose=verbose

    def author(self):
        return 'rgore32'
    def study_group(self):
        return 'rgore32'



    def add_evidence(self, X, Y):
        def generate_leaf_node(sub_dataset):
            ix=1
            avg_value = np.mean(sub_dataset[:, -ix])
            return np.array([['LEAF', avg_value, 'end', 'end']])
        data = np.hstack((X, Y[:, None]))
        def recursively_create_tree(sub_dataset):
            if len(sub_dataset) <= self.leaf_size:
                return generate_leaf_node(sub_dataset)
            feature_shape=1
            random_feature_index = np.random.randint(sub_dataset.shape[feature_shape] - feature_shape)
            ix=0
            if np.all(sub_dataset[:, random_feature_index] == sub_dataset[ix, random_feature_index]):
                return generate_leaf_node(sub_dataset)
            sorted_data = np.array(sorted(sub_dataset, key=lambda row: row[random_feature_index]))

            median_split_value = np.median(sorted_data[:, random_feature_index])
            if np.max(sorted_data[:, random_feature_index]) == median_split_value:
                return generate_leaf_node(sub_dataset)
            left_mask = sorted_data[:, random_feature_index] <= median_split_value
            left_partition = sorted_data[left_mask]
            right_mask = ~left_mask
            right_partition = sorted_data[right_mask]
            left_subtree = recursively_create_tree(left_partition)
            right_subtree = recursively_create_tree(right_partition)
            root_node = [random_feature_index, median_split_value, 1, len(left_subtree) + 1]

            full_tree_structure = np.vstack([root_node, left_subtree, right_subtree])
            return full_tree_structure
        tree = recursively_create_tree(data)
        self.learner = np.array(tree)




    def query(self, inputs):
        return np.array([self.single(input_data) for input_data in inputs])

    def single(self, input_data):
        leaf_node = 'LEAF'
        current_row = 0
        first_ix=0
        while leaf_node not in self.learner[current_row][first_ix]:
            feature_idx, threshold_value, left_offset, right_offset = map(float, self.learner[current_row])
            current_row = current_row + int(left_offset if input_data[int(feature_idx)] <= threshold_value else right_offset)
        return float(self.learner[current_row][first_ix+1])

