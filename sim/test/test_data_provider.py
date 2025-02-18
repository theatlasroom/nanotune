import os

import pytest

import sim
from sim.data_providers import PassthroughDataProvider, QcodesDataProvider, StaticDataProvider
from sim.mock_devices import Pin

simroot = os.path.dirname(os.path.dirname(os.path.abspath(sim.__file__)))

valid_db_path = os.path.join(
    simroot,
    "data",
    "tuning",
    "dot_tuning_sequences.db",
)

class TestQcodesDataProvier:
    def test_valid_1d_data_provider(self):
        """Create a 1D Data provider, and verify that reading from it with
        different input values yields different outputs.
        """

        in1 = Pin("in1")
        data_1d = QcodesDataProvider(
            [in1], valid_db_path, "GB_Newtown_Dev_3_2", 986
        )

        in1.set_value(0.0)
        out0 = data_1d.get_value()

        in1.set_value(-0.5)
        out1 = data_1d.get_value()

        assert out0 != out1

    def test_valid_2d_data_provider(self):
        """Create a 2D Data provider, and verify that reading from it with
        different input values yields different outputs.
        """

        in1 = Pin("in1")
        in2 = Pin("in2")
        data_2d = QcodesDataProvider(
            [in1, in2], valid_db_path, "GB_Newtown_Dev_3_2", 991
        )

        in1.set_value(0.0)
        in2.set_value(0.0)
        out0 = data_2d.get_value()

        in1.set_value(-0.5)
        in2.set_value(-0.5)
        out1 = data_2d.get_value()
        assert out0 != out1

    def test_bad_db_filename(self):
        """Validate the correct error is raised when trying to load a bad
        database.
        """

        with pytest.raises(FileNotFoundError):
            data_1d = QcodesDataProvider(
                [], "bad_database.db", "GB_Newtown_Dev_3_2", 991
            )

    def test_dataset_not_found(self):
        """Validates the correct error is raised if the specified dataset is
        not found in the db.
        """
        with pytest.raises(NameError):
            data_1d = QcodesDataProvider(
                [Pin("in1")],
                valid_db_path,
                "Bad_Experiment_Name",
                986,
            )

        with pytest.raises(NameError):
            data_1d = QcodesDataProvider(
                [Pin("in1")],
                valid_db_path,
                "GB_Newtown_Dev_3_2",
                987654321,
            )

    def test_good_dataset_parameter(self):
        """Validates the data provider uses the specified output parameter from
        the source dataset.
        """

        data_1d = QcodesDataProvider(
            [Pin("in1")],
            valid_db_path,
            "GB_Newtown_Dev_3_2",
            986,
            model_param_name="sr860_2_R_current",
        )

        assert data_1d.get_value() != 0.0

    def test_bad_dataset_parameter(self):
        """Validates that the correct error is raised if the specified parameter
        name is not found in the dataset.
        """

        with pytest.raises(KeyError):
            data_1d = QcodesDataProvider(
                [Pin("in1")],
                valid_db_path,
                "GB_Newtown_Dev_3_2",
                986,
                model_param_name="BAD_PARAM_NAME",
            )

    def test_too_few_input_bindings(self):
        """Validates that the correct error is raised if too few input binds are
        specified for indexing into the specified dataset.
        """

        in1 = Pin("in1")

        with pytest.raises(ValueError):
            # This is a 2D data set, but only 1 input binding is specified
            data_1d = QcodesDataProvider(
                [], valid_db_path, "GB_Newtown_Dev_3_2", 986
            )

        with pytest.raises(ValueError):
            # This is a 2D data set, but only 1 input binding is specified
            data_2d = QcodesDataProvider(
                [in1], valid_db_path, "GB_Newtown_Dev_3_2", 991
            )

    def test_too_many_input_bindings(self):
        """Validates that the correct error is raised if too many input binds
        are specified for indexing into the specified dataset.
        """

        in1 = Pin("in1")
        in2 = Pin("in2")
        in3 = Pin("in3")

        with pytest.raises(ValueError):
            # This is a 2D data set, but only 1 input binding is specified
            data_1d = QcodesDataProvider(
                [in1, in2], valid_db_path, "GB_Newtown_Dev_3_2", 986
            )

        with pytest.raises(ValueError):
            # This is a 2D data set, but only 1 input binding is specified
            data_2d = QcodesDataProvider(
                [in1, in2, in3], valid_db_path, "GB_Newtown_Dev_3_2", 991
            )


class TestStaticDataProvider:

    def test_static_data_provider(self):
        o1 = Pin("O1")
        o1.set_data_provider(StaticDataProvider(3.14))

        assert o1.get_value() == 3.14


class TestPassthroughDataProvider:

    def test_passthrough_data_provider(self):

        def assert_the_same(pin1 : Pin, pin2 : Pin, value: float) -> None:
            assert(pin1.get_value() == value)
            assert(pin2.get_value() == value)

        pin1 = Pin("Pin1")
        pin2 = Pin("Pin2")

        pin2.set_data_provider(PassthroughDataProvider(pin1))
        assert_the_same(pin1, pin2, 0.0)

        pin1.set_value(1.0)
        assert_the_same(pin1, pin2, 1.0)

        pin2.set_value(2.0)
        assert_the_same(pin1, pin2, 2.0)
