import os
import sqlite3


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
        cur.execute('CREATE TABLE Plant(Plant_id INTEGER PRIMARY KEY, '
                    'name TEXT UNIQUE, '
                    'FOREIGN KEY pH REFERENCES pH (pH)'
                    'FOREIGN KEY sunlight REFERENCES plots (sunlight)')
        cur.execute('CREATE TABLE pH(pH INTEGER')
        cur.execute('CREATE TABLE plots(plot_id INTEGER PRIMARY KEY, '
                    'sunlight TEXT, '
                    'FOREIGN KEY pH references pH (pH)')

    def insert_plant(self, name, pH, sunlight,):
        """
        Inserts a plant into the database.

        Returns a dictionary representation of the plant.

        :param name: name of the plant
        :param pH: desired soil pH
        :param sunlight: amount of sunlight needed
        :return: a dict representing the plant
        """
        cur = self.conn.cursor()
        self.insert_pH(pH)
        self.insert_plot(sunlight, pH)
        plot_dict = self.get_plot_by_sunlight(sunlight)
        plot_id = plot_dict['plot_id']
        pH_dict = self.get_pH(pH)

        query = ('INSERT INTO plant(name, pH, sunlight) '
                 'VALUES(?, ?, ?)')

        cur.execute(query, (name, pH, sunlight))
        self.conn.commit()

        return self.get_plant_by_id(cur.lastrowid)

    def get_plant_by_id(self, plant_id):
        """
        Given a plant's primary key, return a dictionary representation of the
        plant, or None if there is no plannt with that primary key.

        :param plant_id: the primary key of the plant
        :return: a dict representing the plant
        """
        cur = self.conn.cursor()

        query = ('SELECT Plant.plant_id as plant_id, Plant.name as name, '
                 'Plant.pH as pH, Plant.sunlight as sunlight, '
                 'plots.plot_id as plot_id, '
                 'FROM Plant, plots '
                 'WHERE Plant.pH = plots.pH '
                 'AND Plant.sunlight = plots.sunlight'
                 'AND Plant.plant_id = ?')

        cur.execute(query, (plant_id,))
        return row_to_dict_or_none(cur)

    def get_all_plants(self):
        """
        Return a list dictionaries representing all of the plants in the
        database.

        :return: a list of dict objects representing plants
        """

        cur = self.conn.cursor()

        query = ('SELECT Plant.plant_id as plant_id, Plant.name as name, '
                 'Plant.pH as pH, Plant.sunlight as sunlight, '
                 'plots.plot_id as plot_id '
                 'FROM Plant, pH '
                 'WHERE Plant.plant_id = pH.plant_id')

        plants = []
        cur.execute(query)

        for row in cur.fetchall():
            plants.append(dict(row))

        return plants

    def insert_plot(self, sunlight, pH):
        """
        Insert a plot into the database if it does not exist.
        Return a dict representation of the plot.

        :param sunlight: amount of sun the plot receives
        :param pH: pH of the soil in the plot
        :return: dict representing the plot
        """
        cur = self.conn.cursor()
        query = 'INSERT INTO plots(sunlight, pH) VALUES(?)'
        cur.execute(query, (sunlight, pH,))
        self.conn.commit()
        return self.get_plots_by_name(sunlight, pH)

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

        return plots

    def get_plots_by_id(self, plot_id):
        """
        Get a dictionary representation of the plot with the given primary
        key. Return None if the plot does not exist.

        :param plot_id: primary key of the plot
        :return: a dict representing the plot, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT plot_id, plots FROM plots WHERE plot_id = ?'
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
        query = 'SELECT plot_id, plots FROM plots WHERE sunlight = ?'
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
        query = 'SELECT plot_id, plots FROM plots WHERE pH = ?'
        cur.execute(query, (pH,))
        return row_to_dict_or_none(cur)

    def delete_plant(self, plant_id):
        """
        Delete the plant with the given primary key.

        :param plant_id: primary key of the plant
        """

        cur = self.conn.cursor()

        query = 'DELETE FROM Plant WHERE plant_id = ?,' \
                'DELETE FROM pH WHERE plant_id = ?'
        cur.execute(query, (plant_id,))

        self.conn.commit()

    def delete_plot(self, plot_id):

        cur = self.conn.cursor()

        query = 'DELETE FROM plots WHERE plot_id = ?,'
        cur.execute(query, (plot_id,))

        self.conn.commit()


if __name__ == '__main__':
    # Here are some rudimentary tests to make sure that it is possible to
    # create a DogDatabase object, insert some breeds, get the breeds, and
    # get None when getting a breed with a non-existent ID. Feel free to add
    # code here to test methods for owners. This code will only be run if you
    # explicitly run this file, and will not be run when the Flask app runs.
    # This is because when the code from this file is imported, __name__ will
    # not be '__main__', but when it is run explicitly it will be '__main__'.

    db = PlantsDatabase('Plants.sqlite')
    db.insert_plot('full, 7')
    db.insert_plot('shade, 8')
    db.insert_plot('partial, 7')
    db.insert_plot('full, 6')

    db.insert_plant('Roses, 7, full')
    db.insert_plant('')

    plots = db.get_all_plots()
    print('List of all plots:', plots)

    plot = db.get_plots_by_id(1)
    print('plot with ID 1:', plot)

    plot = db.get_plots_by_pH(7)
    print('plots with pH 7:', plot)

    plot = db.get_plots_by_sunlight('full')
    print('plots with full sunlight')
