BEGIN TRANSACTION;
INSERT INTO users
VALUES ('user1'),
    ('user2');
INSERT INTO activity (name, parent, alias)
VALUES ('activity1', NULL, NULL),
    ('activity1child', 'activity1', NULL),
    ('activity1alias', 'activity1', 1),
    ('activity2', NULL, NULL),
    ('activity3', NULL, NULL),
    ('activity4', NULL, NULL),
    ('activity5', NULL, NULL),
    ('activity6', NULL, NULL) ('tz_activity', NULL, NULL),
    ('foo', NULL, NULL),
    ('bar', NULL, NULL),
    ('bash', NULL, NULL);
INSERT INTO timelog (
        id,
        time,
        timezone_offset,
        timezone_name,
        activity,
        user,
        backdated
    )
VALUES (
        1,
        '2021-01-01 00:00:00.0',
        0,
        'UTC',
        'activity1',
        'user1',
        NULL
    ),
    (
        2,
        '2021-01-01 01:00:00.0',
        0,
        'UTC',
        'activity2',
        'user1',
        NULL
    ),
    (
        4,
        '2021-01-01 02:00:00.0',
        0,
        'UTC',
        'activity3',
        'user1',
        NULL
    ),
    (
        3,
        '2021-01-01 03:00:00.0',
        0,
        'UTC',
        'activity4',
        'user1',
        NULL
    ),
    (
        5,
        '2021-01-01 04:00:00.0',
        0,
        'UTC',
        'activity5',
        'user1',
        NULL
    ),
    (
        6,
        '2021-01-01 13:00:00.0-8:00',
        -28800,
        'Pacific Standard Time',
        'tz_activity',
        'user1',
        NULL
    ),
    (
        7,
        '2021-01-01 06:00:00.0',
        0,
        'UTC',
        'activity6',
        'user1',
        NULL
    );
COMMIT;