from flask import Flask, g, render_template
import os
import sqlite3
from collections import OrderedDict

app = Flask(__name__)

app.config['DATABASE'] = os.path.join(app.root_path, 'Plants.sqlite')

def connect_db():
    """
    Returns a sqlite connection object associated with the application's
    database file.
    """

    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row

    return conn


def get_db():
    """
    Returns a database connection. If a connection has already been created,
    the existing connection is used, otherwise it creates a new connection.
    """

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db

def row_to_dict_or_none(cur):
    """
    Given a cursor that has just been used to execute a query, try to fetch one
    row. If the there is no row to fetch, return None, otherwise return a
    dictionary representation of the row.

    :param cur: a cursor that has just been used to execute a query
    :return: a dict representation of the next row, or None
    """
    row = cur.fetchone()

    if row is None:
        return None
    else:
        return dict(row)


class PlantsDatabase():

    def __init__(self, sqlite_filename):
        """
        Creates a connection to the database, and creates tables if the
        database file did not exist prior to object creation.

        :param sqlite_filename: the name of the SQLite database file
        """
        if os.path.isfile(sqlite_filename):
            create_tables = False
        else:
            create_tables = True

        self.conn = sqlite3.connect(sqlite_filename)
        self.conn.row_factory = sqlite3.Row

        cur = self.conn.cursor()
        cur.execute('PRAGMA foreign_keys = 1')
        cur.execute('PRAGMA journal_mode = WAL')
        cur.execute('PRAGMA synchronous = NORMAL')

        if create_tables:
            self.create_tables()

    def create_tables(self):

        cur = self.conn.cursor()
        cur.execute('CREATE TABLE fertilizer(fertilizer_id INTEGER PRIMARY KEY, '
                    'fertilizer_type TEXT UNIQUE)')
        cur.execute('CREATE TABLE plots(plot_id INTEGER PRIMARY KEY, '
                     'sunlight TEXT UNIQUE, pH INTEGER, fertilizer_type TEXT, '
                     'FOREIGN KEY (fertilizer_type) REFERENCES fertilizer(fertilizer_type))')
        cur.execute('CREATE TABLE Plant(Plant_id INTEGER PRIMARY KEY, '
                     '   name TEXT UNIQUE, pH INTEGER, fertilizer_type TEXT, sunlight TEXT,'
                     '   FOREIGN KEY (fertilizer_type) REFERENCES fertilizer(fertilizer_type), '
                     '   FOREIGN KEY (sunlight) REFERENCES plots(sunlight))')
        self.conn.commit()

    def insert_plant(self, name, pH, fertilizer_type, sunlight,):
        """
        Inserts a plant into the database.

        Returns a dictionary representation of the plant.

        :param name: name of the plant
        :param pH: desired soil pH
        :param fertilizer_type: desired nutrient
        :param sunlight: amount of sunlight needed
        :return: a dict representing the plant
        """
        cur = self.conn.cursor()
        # self.insert_plot(sunlight, pH, fertilizer_type)
        # plot_dict = self.get_plots_by_sunlight(sunlight)
        # sunlight = plot_dict['sunlight']

        query = ('INSERT OR IGNORE INTO plant(name, pH, fertilizer_type, sunlight) '
                 'VALUES(?, ?, ?, ?)')

        cur.execute(query, (name, pH, fertilizer_type, sunlight))
        self.conn.commit()

        return self.get_plant_by_id(cur.lastrowid)

    def get_plant_by_id(self, Plant_id):
        """
        Given a plant's primary key, return a dictionary representation of the
        plant, or None if there is no plant with that primary key.

        :param plant_id: the primary key of the plant
        :return: a dict representing the plant
        """
        cur = self.conn.cursor()

        query = ('SELECT Plant_id FROM Plant WHERE Plant.Plant_id = ?')

        cur.execute(query, (Plant_id,))
        return row_to_dict_or_none(cur)

    def get_plant_by_name(self, name):
        """
        Given a plant's name, return a dictionary representation of the
        plant, or None if there is no plant with that name.

        :param name: the name of the plant
        :return: a dict representing the plant
        """
        cur = self.conn.cursor()

        query = ('SELECT Plant_id, name FROM Plant WHERE Plant.name = ?')

        cur.execute(query, (name,))
        return row_to_dict_or_none(cur)

    def get_plant_by_fertilzer(self, fertilizer_type):
        """
        Given a fertilizer, return a dictionary representation of the
        plants, or None if there is no plant with that nutrient.

        :param fertilizer_type: the nutrient the plant needs
        :return: a dict representing the plant
        """
        cur = self.conn.cursor()

        query = ('SELECT Plant.fertilizer_type FROM Plant WHERE Plant.fertilizer_type = ?')

        cur.execute(query, (fertilizer_type,))
        return row_to_dict_or_none(cur)

    def get_all_plants(self):
        """
        Return a list dictionaries representing all of the plants in the
        database.

        :return: a list of dict objects representing plants
        """

        cur = self.conn.cursor()

        query = ('SELECT * FROM Plant')

        plants = []
        cur.execute(query)

        for row in cur.fetchall():
            plants.append(dict(row))

        print(plants)
        return plants

    def insert_plot(self, sunlight, pH, fertilizer_type):
        """
        Insert a plot into the database if it does not exist.
        Return a dict representation of the plot.

        :param sunlight: amount of sun the plot receives
        :param fertilizer_type: fertilizer used on the plot
        :param pH: pH of the soil in the plot
        :return: dict representing the plot
        """
        cur = self.conn.cursor()
        self.insert_fertilizer(fertilizer_type)
        query = ('INSERT OR IGNORE INTO plots(sunlight, pH, fertilizer_type) '
                ' VALUES(?, ?, ?)')
        cur.execute(query, (sunlight, pH, fertilizer_type))
        self.conn.commit()
        return self.get_plots_by_sunlight(sunlight)

    def get_all_plots(self):
        """
        Get a list of dictionary representations of all the plots in the
        database.

        :return: list of dicts representing all plots
        """
        cur = self.conn.cursor()

        query = 'SELECT * FROM plots'

        plots = []
        cur.execute(query)

        for row in cur.fetchall():
            plots.append(dict(row))

        print (plots)
        return plots

    def get_plot_by_id(self, plot_id):
        """
        Get a dictionary representation of the plot with the given primary
        key. Return None if the plot does not exist.

        :param plot_id: primary key of the plot
        :return: a dict representing the plot, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT plot_id FROM plots WHERE plot_id = ?'
        cur.execute(query, (plot_id,))
        return row_to_dict_or_none(cur)

    def get_plots_by_sunlight(self, sunlight):
        """
        Get a dictionary representation of the plots that receive a given amount of sunlight.
        Return None if there is no such plot.

        :param sunlight: amounnt of sunlight received
        :return: a dict representing the plot, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT plot_id, sunlight FROM plots WHERE sunlight = ?'
        cur.execute(query, (sunlight,))
        return row_to_dict_or_none(cur)

    def get_plots_by_pH(self, pH):
        """
        Get a dictionary representation of the plots with the given pH.
        Return None if there is no such plot.

        :param pH: pH of the soil
        :return: a dict representing the plot, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT plot_id, pH FROM plots WHERE pH = ?'
        cur.execute(query, (pH,))
        return row_to_dict_or_none(cur)

    def get_plots_by_fertilizer(self, fertilizer_type):
        """
        Get a dictionary representation of the plots with the given fertilzer.
        Return None if there is no such fertilizer.

        :param fertilizer_type: fertilizer used on the plot
        :return: a dict representing the plot, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT plot_id, fertilizer_type FROM plots WHERE fertilizer_type = ?'
        cur.execute(query, (fertilizer_type,))
        return row_to_dict_or_none(cur)

    def insert_fertilizer(self, fertilizer_type):
        """
        Inserts a fertilizer into the database.

        Returns a dictionary representation of the plant.
        :param fertilizer_typetype: which nutrient it contains (nitrogen, phosphorus, potassium)
        :return: a dict representing the fertilizer
        """
        cur = self.conn.cursor()
        query = 'INSERT OR IGNORE INTO fertilizer(fertilizer_type) VALUES(?)'
        cur.execute(query, (fertilizer_type,))
        self.conn.commit()
        return self.get_fertilizer_by_id(cur.lastrowid)

    def get_all_fertilizer(self):
        """
               Get a list of dictionary representations of all the plots in the
               database.

               :return: list of dicts representing all plots
               """
        cur = self.conn.cursor()

        query = 'SELECT * FROM fertilizer'

        fertilizer = []
        cur.execute(query)

        for row in cur.fetchall():
            fertilizer.append(dict(row))

        print(fertilizer)
        return fertilizer


    def get_fertilizer_by_id(self, fertilizer_id):
        """
        Get a dictionary representation of the fertilizer with the given primary
        key. Return None if the fertilizer does not exist.

        :param fertilizer_id: primary key of the fertilizer
        :return: a dict representing the fertilizer, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT fertilizer_id, fertilizer_type FROM fertilizer WHERE Fertilizer_id = ?'
        cur.execute(query, (fertilizer_id,))
        return row_to_dict_or_none(cur)

    def get_fertilizer_by_type(self, fertilizer_type):
        """
        Get a dictionary representation of the fertilizer type.
        Return None if the plot does not exist.

        :param fertilizer_type: type of fertilizer
        :return: a dict representing the fertilizer, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT fertilizer_type, fertilizer_id FROM fertilizer WHERE Fertilizer_type = ?'
        cur.execute(query, (fertilizer_type,))
        return row_to_dict_or_none(cur)

    def delete_plant(self, Plant_id):
        """
        Delete the plant with the given primary key.

        :param plant_id: primary key of the plant
        """

        cur = self.conn.cursor()

        query = 'DELETE FROM Plant WHERE Plant_id = ?,'
        cur.execute(query, (Plant_id,))

        self.conn.commit()

    def delete_plot(self, plot_id):

        cur = self.conn.cursor()

        query = 'DELETE FROM plots WHERE plot_id = ?,'
        cur.execute(query, (plot_id,))

        self.conn.commit()

    def delete_fertilizer(self, fertilizer_id):

        cur = self.conn.cursor()

        query = 'DELETE FROM fertilizer WHERE fertilizer_id = ?,'
        cur.execute(query, (fertilizer_id,))

        self.conn.commit()

    # def delete_pH(self, pH_id):
    #
    #     cur = self.conn.cursor()
    #
    #     query = 'DELETE FROM pH WHERE pH_id = ?,'
    #     cur.execute(query, (pH_id))
    #
    #     self.conn.commit()


if __name__ == '__main__':
    # Here are some rudimentary tests to make sure that it is possible to
    # create a DogDatabase object, insert some breeds, get the breeds, and
    # get None when getting a breed with a non-existent ID. Feel free to add
    # code here to test methods for owners. This code will only be run if you
    # explicitly run this file, and will not be run when the Flask app runs.
    # This is because when the code from this file is imported, __name__ will
    # not be '__main__', but when it is run explicitly it will be '__main__'.
    db = PlantsDatabase('Plants.sqlite')
    db.insert_fertilizer('potassium')
    db.insert_fertilizer('nitrogen')
    db.insert_fertilizer('phosphate')

    db.insert_plot('full', '7', 'potassium')
    db.insert_plot('shade', '8', 'nitrogen')
    db.insert_plot('partial', '7', 'phosphate')
    db.insert_plot('full', '6', 'nitrogen')

    db.insert_plant('Roses', '7', 'potassium', 'full')
    db.insert_plant('Bleeding Hearts', '6', 'phosphate', 'shade')
    db.insert_plant('Peony', '8', 'nitrogen', 'partial')

    plants = db.get_all_plants()
    print('List of all plants:', plants)


    plots = db.get_all_plots()
    print('List of all plots:', plots)

    plot = db.get_plot_by_id(1)
    print('plot with ID 1:', plot)

    plot = db.get_plots_by_pH(7)
    print('plots with pH 7:', plot)

    plot = db.get_plots_by_sunlight('full')
    print('plots with full sunlight', plot)
