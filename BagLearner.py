import numpy as np
#Rohit Gore
class BagLearner(object):


    def __init__(self, learner=object, kwargs={}, bags=20, boost=False, verbose=False):
        self.learners = []
        self.learner = learner
        self.verbose = verbose
        self.bags = bags
        self.boost = boost


        for _ in range(bags):
            inst_learner = self.learner(**kwargs)
            self.learners.append(inst_learner)

    def author(self):
        return "rgore32"
    def study_group(self):
        return "rgore32"


    def add_evidence(self, data_x, data_y):


        data_y = np.atleast_2d(data_y).T if data_y.ndim == 1 else data_y


        for learner in self.learners:
            # Generate bootstrap algorithm indices
            sample_indices = np.random.randint(0, len(data_x), size=len(data_x))

            # Extract bootstrap sample
            bootstrap_x = data_x[sample_indices]
            bootstrap_y = data_y[sample_indices].ravel()  # Flatten y back to 1D


            learner.add_evidence(bootstrap_x, bootstrap_y)

    def query(self, points):

        # Collect predictions from all learners
        vals = [learner.query(points) for learner in self.learners]

        # Convert to numpy array and take the mean across all learners
        return np.mean(vals, axis=0)
