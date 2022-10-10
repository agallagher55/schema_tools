from os import path

SDE = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde"

EDITOR_TRACKING_FIELD_INFO = {
    "ADDBY": {
        "field_type": "TEXT",
        "field_length": 32,
        "field_alias": "Add By"
    },
    "MODBY": {
        "field_type": "TEXT",
        "field_length": 32,
        "field_alias": "Modified By"
    },
    "ADDDATE": {
        "field_type": "DATE",
        "field_length": "",
        "field_alias": "Add Date"
    },
    "MODDATE": {
        "field_type": "DATE",
        "field_length": "",
        "field_alias": "Modified Date"
    },
}

SPATIAL_REFERENCE_FEATURE = path.join(SDE, "SDEADM.LND_hrm_parcel_parks", "SDEADM.LND_hrm_park")

SOURCE_ACCURACY_CODED_VALUES = {
    'AC': 'Computer Assisted Drafting',
    'CG': 'Cogo',
    'DG': 'Digitize',
    'DV': 'Derived',
    'GP': 'Global Position',
    'IN': 'Interactive',
    'PH': 'Photogrammetric',
    'SI': 'Scanned Image',
    'TS': 'Total Station',
    'XY': 'Coordinated Point',
}

PROJECT_DOMAINS = {
    "SpatialDataSubmissionForm_RC_bonus_rate_districts": [
        {
            "LND_RC_BRDname": {
                '1': 'South End Halifax',
                '2': 'Cogswell Redevelopment Lands',
                '3': 'North End Halifax',
                '4': 'North Dartmouth',
                '5': 'Downtown and Central Dartmouth',
                '6': 'Woodside',
                '7': 'Future Growth Nodes'
            },
            "SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES
        }
    ],
    "SpatialDataSubmissionForm_RC_precinct": [
        {
            "LND_RC_PrecinctFcode": {
                'CDDP': 'Downtown Precinct',
                'CDERP': 'Established Residential Precinct',
                'CDLBP': 'Lake Banook Precinct'
            },
            "SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES
        }
    ],
    "SpatialDataSubmissionForm_RC_acc_parking_prohib": [{"SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES}],
    "SpatialDataSubmissionForm_RC_landmark_buildingsites": [{"SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES}],
    "SpatialDataSubmissionForm_RC_LUB_view_corridors": [{"SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES}],
    "SpatialDataSubmissionForm_RC_max_streetwall_height": [{"SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES}],
    "SpatialDataSubmissionForm_RC_SMPS_view_corridors": [{"SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES}],
    "SpatialDataSubmissionForm_RC_transportation_reserve": [{"SourceAccuracy": SOURCE_ACCURACY_CODED_VALUES}]
}
