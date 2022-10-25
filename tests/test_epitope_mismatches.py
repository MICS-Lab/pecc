import os
import pandas as pd

from pecc.epitope_comparison import compute_epitopic_charge
from pecc.output_type import OutputType
from tests.base_loading_for_tests import base_loading


def test_epitope_comparison_details() -> None:
    ## False Positives
    donordf, recipientdf, output_path = base_loading("False Pos")

    compute_epitopic_charge(
        donordf,
        recipientdf,
        output_path,
        OutputType.ONLY_DETAILS,
        True,
        True,
        False,
    )

    output_df_fp: pd.DataFrame = pd.read_csv(f"{output_path}.csv", index_col="Index")

    assert output_df_fp.at[1, "EpMismatches"] == "None"

    list_mismatches_2: list[str] = output_df_fp.at[2, "EpMismatches"].split(", ")
    assert ("37FV_DR" not in list_mismatches_2)
    # Not a mismatch (not in the prediction nor in the true typing)
    assert ("57S_DR" not in list_mismatches_2)
    # This is a false negative (in DRB1*04:05 (true typing) but not in DRB1*04:04 (predicted typing))

    list_mismatches_5: list[str] = output_df_fp.at[5, "EpMismatches"].split(", ")
    assert ("97W_ABC" in list_mismatches_5)
    # Present on B*14:02 (predicted) but not on B*14:10 (true typing) and isn't compensated by loci HLA-A or HLA-C.
    # Therefore is a false positive.

    os.remove(f"{output_path}.csv")


    ## False Negatives
    donordf, recipientdf, output_path = base_loading("False Negs")

    compute_epitopic_charge(
        donordf,
        recipientdf,
        output_path,
        OutputType.ONLY_DETAILS,
        True,
        True,
        False,
    )

    output_df_fn: pd.DataFrame = pd.read_csv(f"{output_path}.csv", index_col="Index")

    for index_ in range(6, 2146):
        assert output_df_fn.at[index_, "EpMismatches"] == "None"

    list_mismatches_1: list[str] = output_df_fn.at[1, "EpMismatches"].split(", ")
    assert ("rq26Y" in list_mismatches_1)
    # rq26Y is in DQB1*03:01 but not in DQB1*03:02 (can be checked by aligning the sequences on
    # https://www.ebi.ac.uk/ipd/imgt/hla/alignment/)
    # The prediction does not output rq26Y although it should
    # rq26Y is therefore a false negative
    assert ("rqp37YA" not in list_mismatches_1)
    # Both have this eplet
    assert ("rp37FV" not in list_mismatches_1)
    # The mismatch is a DQ mismatch and this is a DR / DP eplet

    list_mismatches_2: list[str] = output_df_fn.at[2, "EpMismatches"].split(", ")
    assert ("37FV_DR" not in list_mismatches_2)
    # Not a mismatch (not in the prediction nor in the true typing)
    assert ("57S_DR" in list_mismatches_2)
    # This is a false negative

    list_mismatches_5: list[str] = output_df_fn.at[5, "EpMismatches"].split(", ")
    assert (list_mismatches_5 == ["None"])
    # All the eplet mismatches are compensated by B*35:01

    os.remove(f"{output_path}.csv")


def test_epitope_comparison_count() -> None:
    donordf, recipientdf, output_path = base_loading("False Negs")

    compute_epitopic_charge(
        donordf,
        recipientdf,
        output_path,
        OutputType.COUNT,
        True,
        True,
        False,
    )

    output_df: pd.DataFrame = pd.read_csv(f"{output_path}.csv", index_col="Index")

    for index_ in range(5, 2146):
        # We can include index_ = 5 because we're talking about False Negatives here (all the eplet mismatches are
        # compensated by B*35:01)
        assert output_df.at[index_, "Epitopic Charge"] == 0

    os.remove(f"{output_path}.csv")