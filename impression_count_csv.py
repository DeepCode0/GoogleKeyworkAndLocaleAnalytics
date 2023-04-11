import os
import argparse
import sys
import uuid
import pandas as pd
from flask import Flask, request, jsonify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

app = Flask(__name__)



def add_keyword_plan(client, customer_id,keywords,locale):
    keyword_plan = create_keyword_plan(client, customer_id,keywords,locale)
    print("hello1")
    keyword_plan_campaign = create_keyword_plan_campaign(
        client, customer_id, keyword_plan,keywords,locale
    )
    print("hello2")
    keyword_plan_ad_group = create_keyword_plan_ad_group(
        client, customer_id, keyword_plan_campaign,keywords,locale
    )
    print("hello3")
    create_keyword_plan_ad_group_keywords(
        client, customer_id, keyword_plan_ad_group,keywords,locale
    )
    print("hello4")
    # create_keyword_plan_negative_campaign_keywords(
    #     client, customer_id, keyword_plan_campaign,keywords,locale
    # )
    print("hello5")
    return keyword_plan


def create_keyword_plan(client, customer_id,keywords,locale):
    keyword_plan_service = client.get_service("KeywordPlanService")
    operation = client.get_type("KeywordPlanOperation")
    keyword_plan = operation.create

    keyword_plan.name = f"Keyword plan for traffic estimate {uuid.uuid4()}"

    forecast_interval = (
        client.enums.KeywordPlanForecastIntervalEnum.NEXT_MONTH
    )
    keyword_plan.forecast_period.date_interval = forecast_interval
    print("helloji")
    response = keyword_plan_service.mutate_keyword_plans(
        customer_id=customer_id, operations=[operation]
    )
    print("helloji")
    resource_name = response.results[0].resource_name

    print(f"Created keyword plan with resource name: {resource_name}")

    return resource_name


def create_keyword_plan_campaign(client, customer_id, keyword_plan,keywords,locale):
    """Adds a keyword plan campaign to the given keyword plan.

    Args:
        client: An initialized instance of GoogleAdsClient
        customer_id: A str of the customer_id to use in requests.
        keyword_plan: A str of the keyword plan resource_name this keyword plan
            campaign should be attributed to.create_keyword_plan.

    Returns:
        A str of the resource_name for the newly created keyword plan campaign.

    Raises:
        GoogleAdsException: If an error is returned from the API.
    """
    keyword_plan_campaign_service = client.get_service(
        "KeywordPlanCampaignService"
    )
    operation = client.get_type("KeywordPlanCampaignOperation")
    keyword_plan_campaign = operation.create

    keyword_plan_campaign.name = f"Keyword plan campaign {uuid.uuid4()}"
    keyword_plan_campaign.cpc_bid_micros = 1000000
    keyword_plan_campaign.keyword_plan = keyword_plan

    network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    keyword_plan_campaign.keyword_plan_network = network

    geo_target = client.get_type("KeywordPlanGeoTarget")
    # Constant for U.S. Other geo target constants can be referenced here:
    # https://developers.google.com/google-ads/api/reference/data/geotargets
    for local in locale:
        geo_target.geo_target_constant.canonical_name = local
        keyword_plan_campaign.geo_targets.append(geo_target)

    # Constant for English
    language = "languageConstants/1000"
    keyword_plan_campaign.language_constants.append(language)

    response = keyword_plan_campaign_service.mutate_keyword_plan_campaigns(
        customer_id=customer_id, operations=[operation]
    )

    resource_name = response.results[0].resource_name

    print(f"Created keyword plan campaign with resource name: {resource_name}")

    return resource_name


def create_keyword_plan_ad_group(client, customer_id, keyword_plan_campaign,keywords,locale):
    """Adds a keyword plan ad group to the given keyword plan campaign.

    Args:
        client: An initialized instance of GoogleAdsClient
        customer_id: A str of the customer_id to use in requests.
        keyword_plan_campaign: A str of the keyword plan campaign resource_name
            this keyword plan ad group should be attributed to.

    Returns:
        A str of the resource_name for the newly created keyword plan ad group.

    Raises:
        GoogleAdsException: If an error is returned from the API.
    """
    operation = client.get_type("KeywordPlanAdGroupOperation")
    keyword_plan_ad_group = operation.create

    keyword_plan_ad_group.name = f"Keyword plan ad group {uuid.uuid4()}"
    keyword_plan_ad_group.cpc_bid_micros = 2500000
    keyword_plan_ad_group.keyword_plan_campaign = keyword_plan_campaign

    keyword_plan_ad_group_service = client.get_service(
        "KeywordPlanAdGroupService"
    )
    response = keyword_plan_ad_group_service.mutate_keyword_plan_ad_groups(
        customer_id=customer_id, operations=[operation]
    )

    resource_name = response.results[0].resource_name

    print(f"Created keyword plan ad group with resource name: {resource_name}")

    return resource_name


def create_keyword_plan_ad_group_keywords(client, customer_id, plan_ad_group,keywords,locale):
    """Adds keyword plan ad group keywords to the given keyword plan ad group.

    Args:
        client: An initialized instance of GoogleAdsClient
        customer_id: A str of the customer_id to use in requests.
        plan_ad_group: A str of the keyword plan ad group resource_name
            these keyword plan keywords should be attributed to.

    Raises:
        GoogleAdsException: If an error is returned from the API.
    """
    keyword_plan_ad_group_keyword_service = client.get_service(
        "KeywordPlanAdGroupKeywordService"
    )
    operation = client.get_type("KeywordPlanAdGroupKeywordOperation")
    operations = []

    for keyword in keywords:
        operation = client.get_type("KeywordPlanAdGroupKeywordOperation")
        keyword_plan_ad_group_keyword1 = operation.create
        keyword_plan_ad_group_keyword1.text = keyword
        keyword_plan_ad_group_keyword1.cpc_bid_micros = 2000000
        keyword_plan_ad_group_keyword1.match_type = (
            client.enums.KeywordMatchTypeEnum.BROAD
        )
        keyword_plan_ad_group_keyword1.keyword_plan_ad_group = plan_ad_group
        operations.append(operation)


    response = keyword_plan_ad_group_keyword_service.mutate_keyword_plan_ad_group_keywords(
        customer_id=customer_id, operations=operations
    )

    for result in response.results:
        print(
            "Created keyword plan ad group keyword with resource name: "
            f"{result.resource_name}"
        )


def create_keyword_plan_negative_campaign_keywords(
    client, customer_id, plan_campaign,keywords,locale
):
    """Adds a keyword plan negative campaign keyword to the given campaign.

    Args:
        client: An initialized instance of GoogleAdsClient
        customer_id: A str of the customer_id to use in requests.
        plan_campaign: A str of the keyword plan campaign resource_name
            this keyword plan negative keyword should be attributed to.

    Raises:
        GoogleAdsException: If an error is returned from the API.
    """
    keyword_plan_negative_keyword_service = client.get_service(
        "KeywordPlanCampaignKeywordService"
    )
    operation = client.get_type("KeywordPlanCampaignKeywordOperation")

    keyword_plan_campaign_keyword = operation.create
    keyword_plan_campaign_keyword.text = "moon walk"
    keyword_plan_campaign_keyword.match_type = (
        client.enums.KeywordMatchTypeEnum.BROAD
    )
    keyword_plan_campaign_keyword.keyword_plan_campaign = plan_campaign
    keyword_plan_campaign_keyword.negative = True

    response = keyword_plan_negative_keyword_service.mutate_keyword_plan_campaign_keywords(
        customer_id=customer_id, operations=[operation]
    )

    print(
        "Created keyword plan campaign keyword with resource name: "
        f"{response.results[0].resource_name}"
    )


# if __name__ == "__main__":
#     # GoogleAdsClient will read the google-ads.yaml configuration file in the
#     # home directory if none is specified.
#     googleads_client = GoogleAdsClient.load_from_storage(version="v13")

#     parser = argparse.ArgumentParser(
#         description="Creates a keyword plan for specified customer."
#     )
#     # The following argument(s) should be provided to run the example.
#     parser.add_argument(
#         "-c",
#         "--customer_id",
#         type=str,
#         required=True,
#         help="The Google Ads customer ID.",
#     )
#     args = parser.parse_args()

#     try:
#         main(googleads_client, args.customer_id)
#     except GoogleAdsException as ex:
#         print(
#             f'Request with ID "{ex.request_id}" failed with status '
#             f'"{ex.error.code().name}" and includes the following errors:'
#         )
#         for error in ex.failure.errors:
#             print(f'\tError with message "{error.message}".')
#             if error.location:
#                 for field_path_element in error.location.field_path_elements:
#                     print(f"\t\tOn field: {field_path_element.field_name}")
#         sys.exit(1)

      



@app.route('/forecast', methods=['GET'])
def forecast():
    try:
        # Get the request parameters
        data = request.get_json()
        csv_link = "Example - Sheet1.csv"
        customer_id = data['customer_id']
        # Set up the Google Ads API client
        creds = {
    "developer_token": "v9JjSajUPPZgNkkAeJV2KQ",
    "client_id": "225460967371-540fj6skb81a6gc6jq4pc6j9qt7b5896.apps.googleusercontent.com",
    "client_secret": "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",
    "refresh_token": "1//06O-cMB_EA9XQCgYIARAAGAYSNwF-L9Ir1h7Kolw47wO2EUfTIhIYyljw5cQSkbdhnro3sKh9j5cnrhizoHW7WV_SED21f4XXvy8",
    "use_proto_plus":'false'
}
        
        try:
            csv_data = pd.read_csv(csv_link)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        cities = csv_data.loc[:,"CITY"]
        keywords_arr = csv_data.loc[:,"KEYWORD"]
        impressions_list = []
        print("hello")
        client = GoogleAdsClient.load_from_dict(creds, version='v13')
        print("hello")
        for i,city in enumerate(cities):
            locale = city.split('|')
            keywords = keywords_arr[i].split(',')
            impressions_list.append(10000)
            # keyword_plan = add_keyword_plan(client, (customer_id),keywords,locale)
            # print("hello")
            
            # keyword_plan_service = client.get_service("KeywordPlanService")
            # resource_name = keyword_plan_service.keyword_plan_path(
            #     customer_id, keyword_plan.id
            # )

            # response = keyword_plan_service.generate_forecast_cruve(
            #     keyword_plan=resource_name
            # )
            # print(response)
            # results = []
            # for i, forecast in enumerate(response.keyword_forecasts):
            #     print(f"#{i+1} Keyword ID: {forecast.keyword_plan_ad_group_keyword}")
            #     result = {}
            #     metrics = forecast.keyword_forecast
            #     imp_val = metrics.impressions
            #     impressions = f"{imp_val:.2f}" if imp_val else "unspecified"
            #     # result[forecast.keyword_plan_ad_group_keyword] = impressions
            #     impressions_list.append(impressions)
        
        csv_data['MAX MONTHLY IMPRESSIONS WITH UNLIMITED DAILY BUDGET'] = impressions_list
        csv_data.to_csv(csv_link[:-4]+'copy.csv')


        return jsonify({"success"}), 200
        
    except GoogleAdsException as ex:
        return jsonify({'error': str(ex)}), 500
        
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)




    # Set up the forecast service and request
        # forecast_service = client.get_service('ForecastService')
        # forecast_request = client.get_type('GenerateForecastMetricsRequest')
        # forecast_options = forecast_request.options
        
        # # Set the targeting criteria
        # targeting = forecast_options.keyword_options
        # location = forecast_options.geo_target_options
        # location.geo_targets.append(forecast_options.geo_target_options.geo_target_constant_service.GetGeoTargetConstant(requests=forecast_options.geo_target_options.geo_targets[0].geo_target_constant.id)[0].resource_name)
        
        # # Set the keyword options
        # keyword_options = forecast_options.keyword_options
        # for keyword in keywords:
        #     keyword_info = keyword_options.keyword_infos.add()
        #     keyword_info.text = keyword
        #     keyword_info.match_type = client.get_type('KeywordMatchTypeEnum').EXACT
        
        # # Set the date range
        # date_range = forecast_options.date_interval
        # date_range.start_date.day.value = 1
        # date_range.start_date.month.value = 5
        # date_range.start_date.year.value = 2023
        # date_range.end_date.day.value = 1
        # date_range.end_date.month.value = 6
        # date_range.end_date.year.value = 2023
        
        # # Set the currency code and daily budget
        # money = forecast_options.currency_code
        # money = 'USD'
        # budget = forecast_options.budget_option
        # budget.period_type = client.get_type('ForecastPeriodTypeEnum').MONTHLY
        # budget.daily_amount_micros = int(10000) * 1000000
        
        # # Generate the forecast metrics
        # response = forecast_service.generate_forecast_metrics(request=forecast_request)
        
        # # Extract the forecasted impressions
        # projected_impressions = response.monthly_forecast_metrics[0].max.total_impressions
        
        # # Return the result
        # result = {
        #     'projected_impressions': projected_impressions
        # }

