import pytest, psycopg2.extras, logging, copy
# import load.load_raw as load
from datetime import datetime

# logging setup
logger = logging.getLogger(__name__)

# define test db config to use
TEST_DB_CONFIG = {
    "host": "localhost",
    "port": 5436,
    "dbname": "removebeforeflight_test",
    "user": "removebeforeflight_test",
    "password": "removebeforeflight_test"
}

# mimicked load insert sql
INSERT_SQL = """
        INSERT INTO raw_flight_states 
        (icao24, callsign, origin_country, time_position,
        last_contact, longitude, latitude, baro_altitude,
        on_ground, velocity, true_track, vertical_rate,
        sensors, geo_altitude, squawk, spi,
        position_source, category, fetched_at)
        VALUES %s
    """

@pytest.fixture
def drop_table():
    """Run drop table SQL for instance"""

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS raw_flight_states")
    conn.commit()

    cursor.close()
    conn.close()

@pytest.fixture
def create_table(drop_table):
    """Run create table SQL for instance"""

    SQL = """CREATE TABLE raw_flight_states (
    id SERIAL PRIMARY KEY,
    icao24 VARCHAR(6) NOT NULL,
    callsign VARCHAR(8),
    origin_country VARCHAR(64) NOT NULL,
    time_position BIGINT,
    last_contact BIGINT NOT NULL,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    baro_altitude DOUBLE PRECISION,
    on_ground BOOLEAN NOT NULL,
    velocity DOUBLE PRECISION,
    true_track DOUBLE PRECISION,
    vertical_rate DOUBLE PRECISION,
    sensors INTEGER[],
    geo_altitude DOUBLE PRECISION,
    squawk VARCHAR(4),
    spi BOOLEAN NOT NULL,
    position_source INTEGER NOT NULL,
    category INTEGER,
    fetched_at TIMESTAMP DEFAULT NOW()
)"""
    
    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute(SQL) # create identical raw table in test
    conn.commit()

    cursor.close()
    conn.close()
    logger.info("Create_table fixture complete")

@pytest.fixture
def raw_response():
    """Return mimicked opensky api response without planned appended fetched_at"""

    return [[ # list of lists
        'a5b764', # icao24 0
        'ASA415  ', # callsign 1
        'United States', # origin country 2
        1777764099, # time position 3
        1777764099, # last contact 4
        -110.3579, # long 5
        41.4999, # lat 6
        10363.2, # baro altitude 7
        False, # on ground 8
        220.49, # velocity 9
        306.84, # true track 10
        0, # veritcal rate 11
        None, # sensors (type int[]) 12
        10561.32, # geo altitude 13
        None, # squawk (type String) 14
        False, # spi 15
        0, # position source 16
        6, # category 17
        # fetched_at # fetched_at
    ]]

def test_create_table(create_table):
    """Test table creation via fixture"""

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    # select all tuples (naturally expect 0 tuples after creation)
    cursor.execute("SELECT * FROM raw_flight_states")
    all_tuples = cursor.fetchall() # returns list of all tuples

    # assert 0 records
    assert len(all_tuples) == 0

    # check cols by cursor description
    columns = [table_descrip[0] for table_descrip in cursor.description]

    assert columns[0] == 'id' # primary key for table prepended
    assert columns[1] == 'icao24'
    assert columns[-1] == 'fetched_at' # fetched_at in schema

def test_load(create_table, raw_response):
    """Test loading in db table executes unchanged metadata and types"""

    fetched_at = datetime.now()

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    # mimic load_raw.py load_raw_states(states, fetched_at) with test db connection, cursor

    # comprehend list of tuples for insertion with identical fetched timestamps
    rows = []
    for state in raw_response:
        rows.append(tuple(state) + (fetched_at,))

    # exec and commit rows load with fetched_at metadata
    psycopg2.extras.execute_values(cursor, INSERT_SQL, rows)
    conn.commit()

    # fetch
    cursor.execute("SELECT * FROM raw_flight_states")
    all_tuples = cursor.fetchall()

    # assert loaded data
    assert all_tuples[0][0] == 1 # id
    assert all_tuples[0][1] == 'a5b764' # icao24
    assert all_tuples[0][2] == 'ASA415  ' # callsign 
    assert all_tuples[0][4] == 1777764099
    assert all_tuples[0][6] == -110.3579
    assert all_tuples[0][9] is False
    assert all_tuples[0][10] == 220.49
    assert all_tuples[0][13] is None
    

    # ensure value fetched_at exists
    assert all_tuples[0][-1] is not None
    assert isinstance(all_tuples[0][19], datetime)
    assert len(all_tuples) == 1

    # check cols by cursor description
    columns = [table_descrip[0] for table_descrip in cursor.description]

    assert columns[0] == 'id' # primary key for table prepended
    assert columns[1] == 'icao24'
    assert columns[19] == 'fetched_at' # fetched_at in schema
    
    cursor.close()
    conn.close()

def test_complex_load(create_table, raw_response):
    """Test full field values i.e. all fields present"""

    fetched_at = datetime.now()

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    # deep copy raw response
    raw_full_response = copy.deepcopy(raw_response)

    # fill all fixture nulls
    raw_full_response[0][12] = [101, 202, 303] # sensors
    raw_full_response[0][14] = '4251' # squawk

    rows = []
    for state in raw_full_response:
        rows.append(tuple(state) + (fetched_at,))

    psycopg2.extras.execute_values(cursor, INSERT_SQL, rows)
    conn.commit()

    # fetch distinct cols for check
    cursor.execute("""
        SELECT id, icao24, callsign, sensors, squawk, fetched_at
        FROM raw_flight_states
    """)

    all_tuples_distinct = cursor.fetchall()

    assert all_tuples_distinct[0][0] == 1 # id
    assert all_tuples_distinct[0][1] == 'a5b764'
    assert all_tuples_distinct[0][2] == 'ASA415  '
    assert all_tuples_distinct[0][3] == [101, 202, 303]
    assert all_tuples_distinct[0][4] == "4251"
    assert isinstance(all_tuples_distinct[0][5], datetime)

    assert len(all_tuples_distinct) == 1

    cursor.close()
    conn.close()

def test_load_nulls(create_table, raw_response):
    """Test max nulls where expected loads correctly"""

    fetched_at = datetime.now()

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    # copy raw response
    raw_null_response = copy.deepcopy(raw_response)

    # manipulate fixture copy with max nulls 
    # BEFORE table load (id is prepended then and only then i.e. index shift later)
    raw_null_response[0][1] = None # callsign
    raw_null_response[0][3] = None # time pos
    raw_null_response[0][5] = None # long
    raw_null_response[0][6] = None # lat
    raw_null_response[0][7] = None # baro alt
    raw_null_response[0][9] = None # velocity
    raw_null_response[0][10] = None # true track
    raw_null_response[0][11] = None # vertical rate
    raw_null_response[0][13] = None # geo alt
    raw_null_response[0][17] = None # category

    # comprehend list of tuples for insertion with identical fetched timestamps
    rows = []
    for state in raw_null_response:
        rows.append(tuple(state) + (fetched_at,))

    # exec and commit rows load with fetched_at metadata
    psycopg2.extras.execute_values(cursor, INSERT_SQL, rows)
    conn.commit()

    # fetch records
    cursor.execute("SELECT * FROM raw_flight_states")
    all_tuples = cursor.fetchall()

    # primary key id is prepended, fetched_at is appended
    assert all_tuples[0][1] is not None # icao24 gets shifted by id
    assert all_tuples[0][2] is None # callsign becomes index 2
    assert all_tuples[0][4] is None # time pos
    assert all_tuples[0][6] is None # long
    assert all_tuples[0][7] is None # lat
    assert all_tuples[0][8] is None # baro alt
    assert all_tuples[0][10] is None # velocity
    assert all_tuples[0][14] is None # sensors already None
    assert all_tuples[0][15] is None # squawk already None
    assert all_tuples[0][18] is None # category

    # ensure value fetched_at exists and is of correct type/instance (should be 19 with id prepended)
    assert all_tuples[0][19] is not None
    assert isinstance(all_tuples[0][19], datetime)

    assert len(all_tuples) == 1

    cursor.close()
    conn.close()

def test_invalid_nulls(create_table, raw_response):
    """Test not null constraint failures"""

    fetched_at = datetime.now()

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    # copy raw response
    raw_invalid_response = copy.deepcopy(raw_response)

    # set invalid required field
    raw_invalid_response[0][0] = None

    # append fetched at to each defined tuple
    rows = []
    for state in raw_invalid_response:
        rows.append(tuple(state) + (fetched_at,))

    # expect null violation occurs
    with pytest.raises(psycopg2.errors.NotNullViolation):
        psycopg2.extras.execute_values(cursor, INSERT_SQL, rows)
        conn.commit()

    # rollback commit, check for data inserted
    conn.rollback()

    cursor.execute("""
        SELECT COUNT(*) FROM raw_flight_states
    """)

    row_count = cursor.fetchone()[0]

    assert row_count == 0

    cursor.close()
    conn.close()

def test_batch_load(create_table, raw_response):
    """Test multiple state vectors insert correctly"""

    fetched_at = datetime.now()

    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    # deepcopy raw response fixture
    batch = copy.deepcopy(raw_response)

    # add more state vectors by deepcopying first (only) state vector and manipulating
    second = copy.deepcopy(raw_response[0])
    second[0] = "bbbbbb"
    second[1] = "DAL999  "
    second[2] = "Canada"

    third = copy.deepcopy(raw_response[0])
    third[0] = "cccccc"
    third[8] = True # on ground

    # append state vectors
    batch.append(second)
    batch.append(third)

    # append fetched at to each defined tuple
    rows = []
    for state in batch:
        rows.append(tuple(state) + (fetched_at,))

    psycopg2.extras.execute_values(cursor, INSERT_SQL, rows)
    conn.commit()

    cursor.execute("""
        SELECT COUNT(*) FROM raw_flight_states
    """)

    row_count = cursor.fetchone()[0]

    assert row_count == 3

    # fetch distinct countries for expected manipulation persistence
    cursor.execute("""
        SELECT DISTINCT origin_country FROM raw_flight_states
    """)

    countries = [row[0] for row in cursor.fetchall()]

    assert "United States" in countries
    assert "Canada" in countries

    cursor.close()
    conn.close()