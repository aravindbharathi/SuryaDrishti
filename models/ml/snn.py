import numpy as np

from scipy.interpolate import CubicSpline
from scipy.special import erf

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.optimizers import SGD

from keras.models import load_model
from keras.layers import LeakyReLU
from keras.layers import Dense
from keras.layers import Activation
from keras.models import Sequential
from keras import initializers
from keras import backend as K
from keras.utils.generic_utils import get_custom_objects

from math import exp

tf.device('cpu:0')
ml_dir = os.path.dirname((os.path.realpath(__file__)))


class SNN():
    def __init__(self):
        tf.random.set_seed(0)
        np.random.seed(0)

        self.index = 0

        def custom_activation(x):
            return K.sigmoid(0.05 * x)

        get_custom_objects().update({'custom_activation': Activation(custom_activation)})

        ones_initializer = initializers.Constant(value=100)
        zeros_initializer = initializers.Zeros()

        opt = SGD(learning_rate=0.002)

        self.n = 100
        self.input_dim = 3 * self.n + 3

        self.model = Sequential()
        self.model.add(Dense(128, input_dim=self.input_dim, name='layer1'))
        self.model.add(LeakyReLU(alpha=0.1))
        self.model.add(Dense(32, name='layer2'))
        self.model.add(LeakyReLU(alpha=0.1))
        self.model.add(Dense(1, name='layer3', kernel_initializer=zeros_initializer,
                       bias_initializer=ones_initializer))
        self.model.add(Activation(custom_activation, name='SpecialActivation'))
        self.model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

    def forward(self, input):
        output = self.model(input)
        return output

    def save_chkpt(self):
        self.model.save(os.path.join(ml_dir, 'checkpoint.h5'), overwrite=True,
                        include_optimizer=True, save_format='h5')
        with open(os.path.join(ml_dir, 'index.txt'), 'w') as output:
            output.write(str(self.index))

    def load_chkpt(self):
        self.model = load_model(os.path.join(ml_dir, 'checkpoint.h5'))
        with open(os.path.join(ml_dir, 'index.txt'), 'r') as output:
            self.index = int(output.read(-1))

    def interpolate(self, processed_lc):
        time, rates = processed_lc[:, ~np.isnan(processed_lc[0])]
        spline = CubicSpline(time, rates, extrapolate=True)

        start_time, end_time = time[0], time[-1]
        x = np.linspace(start_time, end_time, num=self.n, endpoint=True)

        return spline(x)

    def EFP(self, params):
        if params['is_detected']:
            if params['fit_params']['is_fit']:
                x = np.linspace(params['start_time'], params['end_time'], num=self.n, endpoint=True)
                A = params['fit_params']['A']
                B = params['fit_params']['B']
                C = params['fit_params']['C']
                D = params['fit_params']['D']

                Z = (2 * B + C**2 * D) / (2 * C)
                EFP_fit = (0.5 * np.sqrt(np.pi) * A * C) \
                    * np.exp(D * (B - x) + C**2 * D**2 / 4) \
                    * (erf(Z) - erf(Z - x / C))
                return EFP_fit
            else:
                return np.ones((self.n,)) * params['bg_rate']
        else:
            return np.ones((self.n,)) * params['bg_rate']

    def train(self, data_list, labels, epochs):
        training_data = np.empty((0, self.input_dim))
        for data in data_list:
            processed_fit = self.interpolate(data['processed_lc'])
            ns_fit = self.EFP(data['params_ns'])
            lm_fit = self.EFP(data['params_lm'])
            psnr = data['psnr']
            ns_chisq = data['params_ns']['fit_params']['ChiSq']
            lm_chisq = data['params_lm']['fit_params']['ChiSq']

            input_data = np.concatenate((processed_fit,
                                         ns_fit,
                                         lm_fit,
                                         np.array([np.log(1 + 1 / ns_chisq),
                                                  np.log(1 + 1 / lm_chisq),
                                                  psnr])
                                         ))
            input_data = np.expand_dims(input_data, axis=0)
            training_data = np.concatenate((training_data, input_data), axis=0)

        bs = min(32, len(training_data))
        history = self.model.fit(training_data, labels, epochs=epochs, verbose=0, batch_size=bs)

        K.set_value(self.model.optimizer.learning_rate, 0.0001 + 0.002 * exp(-0.1 * self.index))
        self.index = self.index + 1

        return history

    def get_conf(self, data_list):
        conf_data = np.empty((0, self.input_dim))
        for data in data_list:
            processed_fit = self.interpolate(data['processed_lc'])
            ns_fit = self.EFP(data['params_ns'])
            lm_fit = self.EFP(data['params_lm'])
            psnr = data['psnr']
            ns_chisq = data['params_ns']['fit_params']['ChiSq']
            lm_chisq = data['params_lm']['fit_params']['ChiSq']

            input_data = np.concatenate((processed_fit,
                                         ns_fit,
                                         lm_fit,
                                         np.array([np.log(1 + 1 / ns_chisq),
                                                  np.log(1 + 1 / lm_chisq),
                                                  psnr])
                                         ))
            input_data = np.expand_dims(input_data, axis=0)
            conf_data = np.concatenate((conf_data, input_data), axis=0)

        return self.model.predict(conf_data).flatten()


if __name__ == '__main__':
    model = SNN()
