import SVHDProvider as dataset
from voxnet.model import get_model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
import os
import numpy as np

data_type = "FPS"   # or TIC

tensorboard_callback = TensorBoard(log_dir=os.path.join("log", data_type))

BATCH_SIZE = 128


def shuffle_data(data, lbl):
    idx = np.arange(len(lbl))
    np.random.shuffle(idx)
    return data[idx, ...], lbl[idx]


def train():
    if os.path.isfile(f"{data_type}_train_data.npz"):
        with np.load(f"{data_type}_train_data.npz") as archive:
            data = archive["data"]
            labels = archive["labels"]
    else:
        data, labels, sample_names = dataset.get_training_data(data_type)
        data = np.stack(data)  # convert to numpy array
        labels = to_categorical(labels)
        np.savez(f"{data_type}_train_data", data=data, labels=labels, sample_names=sample_names)

    if os.path.isfile(f"{data_type}_test_data.npz"):
        with np.load(f"{data_type}_test_data.npz") as archive:
            data_test = archive["data"]
            labels_test = archive["labels"]
    else:
        data_test, labels_test, sample_names = dataset.get_test_data(data_type)
        data_test = np.stack(data_test)  # convert to numpy array
        labels_test = to_categorical(labels_test)
        np.savez(f"{data_type}_test_data", data=data_test, labels=labels_test, sample_names=sample_names)

    data, labels = shuffle_data(data, labels)

    model_path = os.path.join("checkpoints", data_type)
    if not os.path.isdir(model_path):
        os.makedirs(model_path)
    save_checkpoint = ModelCheckpoint(os.path.join(model_path, "model.h5"),
                                      monitor="val_loss", save_best_only=True)

    model = get_model((dataset.SIZE_X, dataset.SIZE_Y, dataset.SIZE_Z, 1), dataset.num_classes(data_type))

    model.summary()
    model.compile(optimizer='rmsprop',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    print("Starting training...")
    log = model.fit(data, labels, epochs=50, batch_size=BATCH_SIZE, validation_data=(data_test, labels_test),
                    verbose=1, callbacks=[save_checkpoint, tensorboard_callback])


if __name__ == "__main__":
    train()
