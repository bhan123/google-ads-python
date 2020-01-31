#!/usr/bin/env python
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This example imports conversion adjustments for existing conversions.

To set up a conversion action, run the add_conversion_action.py example.
"""


import argparse
import sys

from google.ads.google_ads.client import GoogleAdsClient
from google.ads.google_ads.errors import GoogleAdsException


def main(client, customer_id, conversion_action_id, gcl_id, adjustment_type,
         conversion_time, adjustment_time, restatement_value):
    # Determine the adjustment type.
    conversion_adjustment_type_enum = (
        client.get_type('ConversionAdjustmentTypeEnum')
    )
    if adjustment_type.lower() == 'retraction':
        conversion_adjustment_type = conversion_adjustment_type_enum.RETRACTION
    elif adjustment_type.lower() == 'restatement':
        conversion_adjustment_type = conversion_adjustment_type_enum.RESTATEMENT
    else:
        raise ValueError('Invalid adjustment type specified.')

    # Create the conversion adjustment and set basic values.
    conversion_adjustment = (client.get_type('ConversionAdjustment',
                                             version='v2'))
    conversion_action_service = (client.get_service('ConversionActionService',
                                                   version='v2'))
    conversion_adjustment.conversion_action.value = (
        conversion_action_service.conversion_action_path(
            customer_id, conversion_action_id)
    )
    conversion_adjustment.adjustment_type = conversion_adjustment_type
    conversion_adjustment.adjustment_date_time.value = adjustment_time

    # If the restatement value is specified, set it (default currency is USD).
    if (restatement_value and
        conversion_adjustment_type ==
        conversion_adjustment_type_enum.RESTATEMENT):
        conversion_adjustment.restatement_value.adjusted_value.value = (
            restatement_value)
        conversion_adjustment.restatement_value.currency_code.value = 'USD'

    # Set the Gclid Date
    gclid_date_time_pair = client.get_type('GclidDateTimePair', version='v2')
    gclid_date_time_pair.gclid.value = gcl_id
    gclid_date_time_pair.conversion_date_time.value = conversion_time
    conversion_adjustment.gclid_date_time_pair.CopyFrom(gclid_date_time_pair)

    # Try the upload
    conversion_adjustment_upload_service = (
        client.get_service('ConversionAdjustmentUploadService', version='v2')
    )

    try:
        response = (
            conversion_adjustment_upload_service.
            upload_conversions_adjustments(customer_id,
                                           [conversion_adjustment],
                                           partial_failure=True)
        )
        uploaded_conversion_adjustment = (response.results[0])
        print(f'Uploaded conversion that occurred at '
              f'"{uploaded_conversion_adjustment.conversion_date_time.value}" '
              f'from Gclid "{uploaded_conversion_adjustment.gclid.value}" '
              f'to "{uploaded_conversion_adjustment.conversion_action.value}"')

    except GoogleAdsException as ex:
        print(f'Request with ID "{ex.request_id}" failed with status '
              f'"{ex.error.code().name}" and includes the following errors:')
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f'\t\tOn field: {field_path_element.field_name}')
        sys.exit(1)


if __name__ == '__main__':
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = GoogleAdsClient.load_from_storage()

    parser = argparse.ArgumentParser(
        description='Upload an offline conversion.')
    # The following argument(s) should be provided to run the example.
    parser.add_argument('-c', '--customer_id', type=str,
                        required=True, help='The Google Ads customer ID.')
    parser.add_argument('-a', '--conversion_action_id', type=str,
                        required=True, help='The conversion action ID.')
    parser.add_argument('-g', '--gcl_id', type=str,
                        required=True, help='The Google Click Identifier ID.')
    parser.add_argument('-d', '--adjustment_type', type=str,
                        required=True, help='The Adjustment type.')
    parser.add_argument('-t', '--conversion_time', type=str,
                        required=True, help='The conversion time.')
    parser.add_argument('-v', '--adjustment_time', type=str,
                        required=True, help='The adjustment time.')
    args = parser.parse_args()
    # Optional: Specify an adjusted value for adjustment type RESTATEMENT.
    # This value will be ignored if you specify RETRACTION as adjustment type.
    RESTATEMENT_VALUE = None

    main(google_ads_client, args.customer_id, args.conversion_action_id,
         args.gcl_id, args.adjustment_type, args.conversion_time,
         args.adjustment_time, RESTATEMENT_VALUE)
