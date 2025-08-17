check dbt_project.yml inside astro container, there is a problem with the materialized, parsing something weird
get sudo password for astro, not needed. solved

https://github.com/tayljordan/ports/blob/main/ports.json

What Can We Do With This Data?
Even though there are lots of NULL values, still have useful fields:


user_id / imo_number	Identify ships (though many IMO numbers are 0, which is common in some regions or small vessels).
name	You can profile fleets, filter, or cluster by name patterns.
vessel_description	Group by vessel types, do fleet composition analysis.
destination	Text mining / standardization of port names or routes.
eta_timestamp	You can analyze planned arrivals (e.g., which vessels have upcoming ETAs).
latitude, longitude	Currently null, but when available, you can map positions.

So even with this partial data, we can:

Do fleet profiling (e.g., most common vessel types)

Create stats per vessel type (how many, with/without destination, ETA, etc.)

Look at planned arrivals using eta_timestamp

Use destination as a proxy to analyze trade patterns, once standardized.

Why So Many Nulls?
Let’s go field-by-field for likely causes:

Field	Cause of Nulls
latitude, longitude	Possibly filtered out earlier due to not null tests; maybe source data lacks GPS updates.
speed_over_ground, navigational_status	Same as above; either missing in the source or excluded via cleaning.
eta_timestamp	Either malformed (e.g., 29 Feb in non-leap years) or month/day = 0 (which you're discarding).
destination	Empty strings or missing data from the AIS feed.
imo_number = 0	Often means: vessel not required to report IMO (e.g., small, domestic ships).

This is expected in real-world AIS data. The protocol is designed to handle a wide range of ship types, and compliance isn't perfect.

How to Infer the Country?

From user_id (aka MMSI)
MMSI = Maritime Mobile Service Identity

First 3 digits of MMSI = MID (Maritime Identification Digits) → country.

For example:

316006988 → 316 = Canada

367003410 → 367 = USA

440002290 → 440 = South Korea

So:
create a country lookup seed with MID → Country Name, and left join it on LEFT(user_id, 3)::int.
