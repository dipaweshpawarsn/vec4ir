# from gensim.models import Doc2Vec
from .base import RetrievalBase, RetriEvalMixIn
from .word2vec import filter_vocab
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
import numpy as np


class Doc2VecRetrieval(RetrievalBase, RetriEvalMixIn):
    def __init__(self,
                 # model,
                 vocab_analyzer=None,
                 name=None,
                 verbose=0,
                 oov=None,
                 **kwargs):
        # self.model = model
        self.verbose = verbose
        self.oov = oov
        if name is None:
            name = "paragraph-vectors"

        self._init_params(name=name, **kwargs)
        if vocab_analyzer is not None:
            self.analyzer = vocab_analyzer
        else:
            #  use analyzer of matching
            self.analyzer = self._cv.build_analyzer()

    def fit(self, docs, y):
        self._fit(docs, y)
        assert len(docs) == len(y)
        X = [TaggedDocument(self.analyzer(doc),
                            label)
             for doc, label in zip(docs, y)]
        if self.verbose > 0:
            print("Training doc2vec model")
        self.model = Doc2Vec(X,
                             dm=1,
                             size=100,
                             window=8,
                             min_count=1,
                             sample=1e5,
                             workers=16,
                             negative=20,
                             iter=20,
                             dm_concat=1,
                             dm_tag_count=1)
        if self.verbose > 0:
            print("Finished.")

        # self._X = np.asarray([filter_vocab(self.model, x, oov=self.oov) for x in X])
        self._X = np.asarray(X)  # does not filter out of vocabulary words
        return self

    def query(self, query, k=1):
        model = self.model
        indices = self._matching(query)
        docs, labels = self._X[indices], self._y[indices]

        q = self.analyzer(query)

        similarities = []
        for d in docs:
            print("d:", d)
            print("q:", q)
            qv = model.infer_vector(q)
            print("qv:", qv)
            sim = model.similarity(model[model.docvecs[d[1]]], qv)
            print("sim:", sim)
            similarities.append(sim)

        # similarities = [model.similarity(d, model.infer_vector(q)) for d in
        #                 docs]
        ind = np.argsort(np.asarray(similarities))[::-1]  # REVERSE! we want similar ones
        y = labels[ind]
        return y
