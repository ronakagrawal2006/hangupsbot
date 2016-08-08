import nltk, re, pprint
import sys
import os
import csv
import argparse
from nltk.stem.snowball import SnowballStemmer
import random
from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

CURR_PATH = os.path.dirname(__file__)
module_path = os.path.abspath(os.path.join(CURR_PATH, '..'))
sys.path.append(module_path)


# BEFORE DEPLOYING TRAIN ON ALL DATA
class Glados(object):
    def __init__(self, data_filename=None):

        # file_to_train = 'res/training.txt'
        file_to_train = "leaves.txt"  # trainingFile#'res/rewards.txt'
        # file_to_train = 'res/leaves.txt'
        # file_to_train = 'res/leaves.txt'

        self.stemmer = SnowballStemmer("english")
        # if isEmpty(data_filename):
        #     data_filename = os.path.join(CURR_PATH, file_to_train)

        self.data_filename = "leaves.txt"
        print("DATA FILE NAME:" + self.data_filename)
        self.classifier = self.train_and_get_classifer(data_filename)

    """
    Public api
    input: user question text
    output: answer
    """

    def get_help(self, question):
        features = self.extract_feature(question)
        print("Features for Question")
        print(features)
        answer = self.classifier.classify(features)
        prob = self.classifier.prob_classify(features).prob(answer)
        print("---FEATURES-----")
        # print(features)
        # print(features.values())
        print("Probability of answer")
        print(self.classifier.prob_classify(features).prob(answer))  # probability of answer
        response = dict(question=question, answer=answer, probility=prob)
        test_leave_info = {
            'name': 'Kitkat',
            'annual_leaves': 15,
            'optional_leaves': 1,
            'rem_annual': 9,
            'rem_optional': 1,
            'carry_forward': 34
        }
        response = response['answer'] % test_leave_info
        return response

    def train_and_get_classifer(self, data_filename):

        split_ratio = 0.8

        data = self.get_content(data_filename)
        data_set = self.extract_feature_from_doc(data)
        print("data_set", data_set)

        random.shuffle(data_set)
        data_length = len(data)

        train_split = int(data_length * split_ratio)
        training_data = data_set[:train_split]
        test_data = data_set[train_split:]

        log('\n'.join([str(x) for x in data_set]))

        classifier, classifier_name, test_set_accuracy, training_set_accuracy = self.train_using_max_entropy(
            training_data, test_data)

        # print(classifier.most_informative_features())

        # output_file = open(os.path.join(CURR_PATH,"res/accuracy.txt"), "a")
        # output_file.write("\n%s\t\t%s\t\t\t%.8f\t\t%.8f" % (classifier_name, data_length, training_set_accuracy, test_set_accuracy))
        # output_file.close()

        return classifier

    def train_using_naive_bayes(self, training_data, test_data):
        classifier = nltk.NaiveBayesClassifier.train(training_data)
        classifier_name = type(classifier).__name__
        training_set_accuracy = nltk.classify.accuracy(classifier, training_data)
        test_set_accuracy = nltk.classify.accuracy(classifier, test_data)
        return classifier, classifier_name, test_set_accuracy, training_set_accuracy

    def train_using_decision_tree(self, training_data, test_data):
        # entropy_cutoff=0.1,support_cutoff=0.7 gives awesomeresults
        classifier = nltk.classify.DecisionTreeClassifier.train(training_data, entropy_cutoff=0.1, support_cutoff=0.7)
        # print(classifier)
        # print(classifier.pretty_format(width=70, prefix='', depth=4))
        classifier_name = type(classifier).__name__
        training_set_accuracy = nltk.classify.accuracy(classifier, training_data)
        test_set_accuracy = nltk.classify.accuracy(classifier, test_data)
        return classifier, classifier_name, test_set_accuracy, training_set_accuracy

    def train_using_max_entropy(self, training_data, test_data):
        classifier = nltk.maxent.ConditionalExponentialClassifier.train(training_data, algorithm='megam')
        classifier_name = type(classifier).__name__
        training_set_accuracy = nltk.classify.accuracy(classifier, training_data)
        test_set_accuracy = nltk.classify.accuracy(classifier, test_data)
        return classifier, classifier_name, test_set_accuracy, training_set_accuracy

    def train_using_SklearnClassifier(self, training_data, test_data):
        #   Giving bad results. Don't use.
        classifier = SklearnClassifier(BernoulliNB()).train(training_data)
        classifier2 = SklearnClassifier(SVC(), sparse=False).train(training_data)
        print(classifier)
        classifier_name = type(classifier).__name__
        training_set_accuracy = nltk.classify.accuracy(classifier, training_data)
        training_set_accuracy2 = nltk.classify.accuracy(classifier2, training_data)
        test_set_accuracy = nltk.classify.accuracy(classifier, test_data)
        test_set_accuracy2 = nltk.classify.accuracy(classifier2, test_data)
        print(">>>>>>>>")
        print(training_set_accuracy, test_set_accuracy)
        print(training_set_accuracy2, test_set_accuracy2)
        return classifier, classifier_name, test_set_accuracy, training_set_accuracy

    def extract_feature_from_doc(self, document):
        features = []
        for (text, category, answer) in document:
            sent_features = self.extract_feature(text)
            # features.append((sent_features, category))
            features.append((sent_features, answer))
        return features

    def extract_feature(self, text):
        words = self.preprocess(text)
        tags = [nltk.pos_tag(sent) for sent in words]
        sent_keys = self.extract_keys(tags)
        stemmed_words = [self.stemmer.stem(x) for x in sent_keys]
        return self.get_feature_set(stemmed_words)

    def preprocess(self, sentence):
        sentence = sentence.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(sentence)
        filtered_words = [w for w in tokens if not w in stopwords.words('english')]
        return " ".join(filtered_words)

    def extract_keys(self, sentences):
        sent_keys = []
        for sent in sentences:
            keys = [x for (x, n) in sent if n == 'NN' or n == 'VBN']
            if len(keys) == 0:
                keys = [x for (x, n) in sent]
            sent_keys.extend(keys)
        return sent_keys

    def get_feature_set(self, sent_keys):
        return {'keywords': ''.join(sent_keys)}

    def get_content(self, filename):
        test_doc = "hangupsbot/handlers/leaves.txt"  # os.path.join(filename)
        with open(test_doc, 'r') as content_file:
            lines = csv.reader(content_file, delimiter='|')
            res = [x for x in lines if len(x) == 3]
            return res


DEBUG = True
trainingFile = 'res/leaves.txt'  # 'res/rewards.txt'
trainingDataFile = '../../core/res/leaves.txt'  # '../../core/res/ rewards.txt'


def log(msg):
    global DEBUG
    global trainingFile
    global trainingDataFile
    if DEBUG == True: print(msg)


def scanArgs():
    global DEBUG
    parser = argparse.ArgumentParser(description='Glados virtual help engine')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug log output')
    args = parser.parse_args()
    DEBUG = args.debug


if __name__ == '__main__':
    scanArgs()
    account_info = {
        'name': 'John',
        'balance': 323710.38,
        'account_no': 12900989124,
        'phone': 73710203,
        'leave_balance': 30
    }

    glados = Glados()
    ans = glados.get_help('Tell my leave balance.')
    if len(ans) > 0:
        print(ans['answer'] % account_info)

    else:
        print("Unable to understand your request. Please try again")
        # print(classifier.show_most_informative_features(5))
        # print(glados.get_help('what different credit cards you provide?'))
