#    Copyright 2020 Neal Lathia
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from pathlib import PosixPath, Path
import os

import pytest
from modelstore.model_store import ModelStore
from modelstore.storage.states.model_states import ReservedModelStates
from modelstore.utils.exceptions import (
    ModelExistsException,
    ModelNotFoundException,
    ModelNotFoundException,
)

# pylint: disable=missing-function-docstring


@pytest.fixture
def model_store(tmp_path: PosixPath):
    return ModelStore.from_file_system(root_directory=str(tmp_path))


@pytest.fixture
def model_file(tmp_path: PosixPath):
    file_path = os.path.join(tmp_path, "model.txt")
    Path(file_path).touch()
    return file_path


def test_model_not_found(model_store: ModelStore):
    with pytest.raises(ModelNotFoundException):
        model_store.get_model_info("missing-domain", "missing-model")


def test_model_exists(model_store: ModelStore, model_file: str):
    domain = "test-domain"
    model_id = "test-model-id-1"

    # No models = domain not found = model doesn't exist
    assert not model_store.model_exists(domain, model_id)

    # Domain exists, but the model does not
    model_store.upload(domain, "test-model-id-2", model=model_file)
    assert not model_store.model_exists(domain, model_id)

    # Model exists
    model_store.upload(domain, model_id, model=model_file)
    assert model_store.model_exists(domain, model_id)


def test_model_upload_doesnt_overwrite_existing_model(
    model_store: ModelStore, model_file: str
):
    domain = "test-domain"
    model_id = "test-model-id-1"
    model_store.upload(domain, model_id, model=model_file)

    with pytest.raises(ModelExistsException):
        model_store.upload(domain, model_id, model=model_file)


def test_model_upload_overwrites_deleted_model(
    model_store: ModelStore, model_file: str
):
    domain = "test-domain"
    model_id = "test-model-id-1"
    model_store.upload(domain, model_id, model=model_file)
    model_store.delete_model(domain, model_id, skip_prompt=True)
    model_ids = model_store.list_models(domain, ReservedModelStates.DELETED.value)
    assert model_id in model_ids

    model_store.upload(domain, model_id, model=model_file)
    model_ids = model_store.list_models(domain, ReservedModelStates.DELETED.value)
    assert model_id not in model_ids
