# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import os
import logging
from functools import lru_cache
from flask import Flask, request, jsonify
from google_sheet.gs_module import GoogleSheet
from config_data.config import services_data, equipments_data

gs = GoogleSheet()

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route('/notify', methods=['POST'])
def notify_change():
    sheet_name = request.form.get('sheetName')
    message = f"Received notify_change request with sheetName: {sheet_name}"
    app.logger.info(message)
    print(message)

    if not sheet_name:
        warning_msg = "sheetName parameter missing in the request"
        app.logger.warning(warning_msg)
        print(warning_msg)
        return "sheetName parameter missing", 400

    update_cache(sheet_name)
    info_msg = f"Cache updated for sheetName: {sheet_name}"
    app.logger.info(info_msg)
    print(info_msg)

    return "Notification received", 200


@app.route('/get_cached_equipments', methods=['GET'])
def get_cached_equipments():
    return jsonify(fetch_equipments())

@app.route('/get_cached_services', methods=['GET'])
def get_cached_services():
    return jsonify(fetch_services())



@lru_cache(maxsize=50)
def fetch_equipments():
    data = gs.fetch_data(equipments_data)
    app.logger.info(f"Fetched data from {equipments_data}: {data}")
    return data #  gs.fetch_data(equipments_data)


@lru_cache(maxsize=50)
def fetch_services():
    return gs.fetch_data(services_data)


def update_cache(sheet_name):
    message = f"Update cache called for sheetName: {sheet_name}"
    app.logger.info(message)
    
    if sheet_name == equipments_data:
        clear_msg = f"Clearing cache for equipments"
        app.logger.info(clear_msg)
        fetch_equipments.cache_clear()
        fetch_equipments()

    if sheet_name == services_data:
        clear_msg = f"Clearing cache for services"
        app.logger.info(clear_msg)
        fetch_services.cache_clear()
        fetch_services()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
