import wordprep
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os.path

def get_train_data(words, intents, intent_pairs):
    """Builds training data and labels.

    Args:
        words: All words and vocubulary.
        intents: Intents.
        intent_pairs: Combination of patterns and intents.

    Returns:
        Training datasets.
    """
    # Compiles training inputs and labels
    model_in, labels = wordprep.build_training_bag(words, intents, intent_pairs)
    # Packs everything into one tf Dataset and shuffles and batches the data
    training = tf.data.Dataset.from_tensor_slices((model_in,labels)).shuffle(100).batch(5)
    return training

def build_chat_model(vocab_size, intents_size):
    """Builds and compiles a tensorflow model.

    Args:
        vocab_size: Number of words in vocabulary
        intents_size: Number of intents

    Returns:
        Compiled model.
    """
    # Model Definition
    model = Sequential()
    model.add(Dense(128, input_shape=(vocab_size,), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(intents_size, activation='softmax'))

    # Optimizer Settings
    adam = Adam(learning_rate=0.01, decay=1e-6)
    # Compile Model
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
    print(model.summary())
    return model

def model_prep(words, intents, intent_pairs):
    """Loads an existing model or builds and trains a new one.

    Args:
        words: All words and vocubulary.
        intents: Intents.
        intent_pairs: Combination of patterns and intents.

    Returns:
        Compiled model.
    """
    # Checks if saved model exists
    if os.path.exists('data/saved_model/intent_model'):
        # Loads existing saved model
        print("Loading saved model...")
        intent_model = tf.keras.models.load_model('data/saved_model/intent_model')
    else:
        # Trains a new model
        print('Training new model...')
        train_data = get_train_data(words, intents, intent_pairs)
        intent_model = build_chat_model(len(words), len(intents))
        hist = intent_model.fit(train_data, epochs=200, verbose=1)
        intent_model.save('data/saved_model/intent_model')
    print("Intent model loading complete!")
    return intent_model