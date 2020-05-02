from flask import Flask, g, jsonify, request, render_template
from flask.views import MethodView
import os
import requests
import sys
from Plants_db import PlantsDatabase

app = Flask(__name__)

app.config['DATABASE'] = os.path.join(app.root_path, 'Plants.sqlite')

def get_db():
    """
    Returns a PlantsDatabase instance for accessing the database. If the database
    file does not yet exist, it creates a new database.
    """

    if not hasattr(g, 'Plants_db'):
        g.Plants_db = PlantsDatabase(app.config['DATABASE'])

    return g.Plants_db


class RequestError(Exception):
    """
    This custom exception class is for easily handling errors in requests,
    such as when the user provides an ID that does not exist or omits a
    required field.

    We inherit from the Exception class, which is the base Python class that
    provides basic exception functionality. Our custom exception class takes
    a status code and error message in its initializer, and then has a
    to_response() method which creates a JSON response. When an exception of
    this type is raised, the error handler will take care of sending the
    response to the client.
    """

    def __init__(self, status_code, error_message):
        # Call the super class's initializer. Unlike in C++, this does not
        # happen automatically in Python.
        super().__init__(self)

        self.status_code = str(status_code)
        self.error_message = error_message

    def to_response(self):
        """
        Create a Response object containing the error message as JSON.

        :return: the response
        """

        response = jsonify({'error': self.error_message})
        response.status = self.status_code
        return response


@app.errorhandler(RequestError)
def handle_invalid_usage(error):
    """
    Returns a JSON response built from a RequestError.

    :param error: the RequestError
    :return: a response containing the error message
    """
    return error.to_response()

@app.route('/')
def main():
    return render_template('Colin_2020_cs_project_page.html')

class PlotsView(MethodView):
    """
    This view handles all the /plots requests.
    """

    def get(self, plot_id):
        """
        Handle GET requests.

        Returns JSON representing all of the plots if plot_id is None, or a
        single plot if plot_id is not None.

        :param plot_id: id of a plot, or None for all plots
        :return: JSON response
        """
        if plot_id is None:
            plot = get_db().get_all_plots()
            return jsonify(plot)
        else:
            plot = get_db().get_plot_by_id(plot_id)

            if plot is not None:
                response = jsonify(plot)
            else:
                raise RequestError(404, 'plot not found')

            return response

    def post(self):
        """
        Implements POST /plots

        Requires the form parameters 'sunlight', and 'pH'

        :return: JSON response representing the new plot
        """

        for parameter in ('sunlight', 'pH', 'fertilizer_type'):
            if parameter not in request.form:
                error = 'parameter {} required'.format(parameter)
                raise RequestError(422, error)

        plot = get_db().insert_plot(request.form['sunlight'], request.form['pH'],
                                    request.form['fertilizer_type'])
        return jsonify(plot)

    def delete(self, plot_id):
        """
        Handle DELETE requests. The plot_id must be provided.

        :param plot_id: id of a plot
        :return: JSON response containing a message
        """
        if get_db().get_plot_by_id() is None:
            raise RequestError(404, 'plot not found')

        get_db().delete_plot(plot_id)

        return jsonify({'message': 'plot deleted successfully'})


class fertilizerView(MethodView):
    """
    This view handles all the /fertilizer requests.
    """

    def get(self, fertilizer_id):
        """
        Handle GET requests.

        Returns JSON representing all of the plants if plant_id is None, or a
        single plant if plant_id is not None.

        :param fertilizer_id: id of a fertilizer, or None for all fertilizers
        :return: JSON response
        """
        if fertilizer_id is None:
            fertilizer_id = get_db().get_all_fertilizer()
            return jsonify(fertilizer_id)
        else:
            fertilizer_id = get_db().get_plant_by_id(fertilizer_id)

            if fertilizer_id is not None:
                response = jsonify(fertilizer_id)
            else:
                raise RequestError(404, 'fertilizer not found')

            return response


class PlantsView(MethodView):
    """
    This view handles all the /plants requests.
    """

    def get(self, plant_id):
        """
        Handle GET requests.

        Returns JSON representing all of the plants if plant_id is None, or a
        single plant if plant_id is not None.

        :param plant_id: id of a dplantog, or None for all plants
        :return: JSON response
        """
        if plant_id is None:
            plants = get_db().get_all_plants()
            return jsonify(plants)
        else:
            plant = get_db().get_plant_by_id(plant_id)

            if plant is not None:
                response = jsonify(plant)
            else:
                raise RequestError(404, 'plant not found')

            return response

    def post(self):
        """
        Implements POST /plants

        Requires the form parameters 'plant', 'pH', and 'sunlight'

        :return: JSON response representing the new dog
        """

        for parameter in ('plant', 'pH', 'sunlight', 'fertilizer_type'):
            if parameter not in request.form:
                error = 'parameter {} required'.format(parameter)
                raise RequestError(422, error)

        plant = get_db().insert_plant(request.form['plant'], request.form['pH'],
                        request.form['sunlight'], request.form['fertilizer_type'])
        return jsonify(plant)

    def delete(self, plant_id):
        """
        Handle DELETE requests. The plant_id must be provided.

        :param plant_id: id of a dog
        :return: JSON response containing a message
        """
        if get_db().get_plant_by_id(plant_id) is None:
            raise RequestError(404, 'plant not found')

        get_db().delete_plant(plant_id)

        return jsonify({'message': 'plant deleted successfully'})

#Register PlantsView as the handler for all the /plants requests
plants_view = PlantsView.as_view('plants_view')
app.add_url_rule('/plants', defaults={'plant_id': None},
                 view_func=plants_view, methods=['GET', 'DELETE'])
app.add_url_rule('/plants', view_func=plants_view, methods=['POST'])
app.add_url_rule('/plants/<int:Plant_id>', view_func=plants_view, methods=['GET', 'DELETE'])

#Register PlotsView as the handler for all the /plots requests
plots_view = PlotsView.as_view('plots_view')
app.add_url_rule('/plots', defaults={'plot_id': None},
                 view_func=plots_view, methods=['GET', 'DELETE'])
app.add_url_rule('/plots', view_func=plots_view, methods=['POST'])
app.add_url_rule('/plots/<int:plot_id>', view_func=plots_view, methods=['GET', 'DELETE'])

#Register fertilizerView as the handler for all the /fertilizer requests
fertilizer_view = fertilizerView.as_view('fertilizer_view')
app.add_url_rule('/fertilizer', defaults={'fertilizer_id': None},
                 view_func=fertilizer_view, methods=['GET'])
app.add_url_rule('/fertilizer/<int:fertilizer_id>', view_func=fertilizer_view, methods=['GET'])

if __name__ == '__main__':
        app.run(debug=True)