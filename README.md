# SiteBuster


## Vision
The intent of this tool is, similar to DirBuster, to comb for information from a remote source.

As DirBuster combs a webserver for all "directories"
SiteBuster combs a website for all information of a type.

Specifically, it crawls the website and searches for a regex-defined string, storing the output for analysis.

Currently it supports email addresses, and will be expanded to also include phone numbers

## Use 

The intended functionality of this tool is to assist in information gathering for various attacks against a large organization.

The full ambition is a tool which assists with gathering many forms of information, to assist in any variety of manners.

Currently it can be used to harvest email addresses.

## Example

A large organization, such as a college, has a complex assortment of thousands of webpages, with a networking of links connecting them all. Directory pages for every department are available, with large wealths of information stored throughout it all.

A tool which carefully combed the entire website and created a master list of emails, for example, could subsequently be used for **skimming attacks**. Out of the hundreds of faculty at a college, some of them must use bogus passwords. Out of the hundreds of faculty at many different colleges, some must use bogus passwords for their personal email addresses, which are occasionally linked on personal websites.

This ignores MFA and other security procedures which may be in place.

A more sophisticated use would be as an initial information gathering tool to facilitate phishing


# Feature Expansions

- search for any regex-defined string
- provide more information about webpages which are deemed useful
- contain MANY tweaks to allow performance optimization as well as detection evasion
- emulate a human as it performs it search, including spoofing user agent, cookies, and the like
- create a directed graph with weighted vertices mapping the entire website, output to something like Gephi in a human readable format
    - vertices would be weighted by frequency of matched query

# Technical discussion

- Tool must be multithreaded.
- Python is OK because speed of the remote server will be a limiting factor.
- Behavioral tweaks should be modeled after nmap and similar tools, they know what features are needed.
- Tool will need to be completed in stages, base functionality (no detection evasion just yet) is in progress.
- Utilizing an actual browser to perform each request will be too slow, browser must be emulated with proper HTTP metadata.
- Each connection should come from a different ip address.

# Acknowledgements

codebase (heavily rewritten) originated as a messy final project, by Brandi Durham and myself completed during our Operating Systems class at College of Charleston.
-
