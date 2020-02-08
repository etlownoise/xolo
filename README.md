 [XOLO] 
--------
![Xolo Logo](/static/icons/xolo-logo.png)

Author: ET Lownoise 
Version: 1.0

Tool to crawl, visualize and interact with SQL server links in a d3 graph to help in your 
red/blue/purple/.../assessments team exercises. 

Requirements:
-------------

	Requests==2.18.4

	Flask==0.12.2

	Json
	Pypyodbc
	beautifulsoup4==4.6.0

	lxml==4.1.0

	Example:
		pip install pypyodbc
		python -m pip install pypyodbc

Install/Run:
------------
	- Download
	- Decompress 
	- Put it in directory
	- Run it
	
		c:\xolo>python main.py
 		...
 		* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

	- Open your browser http://127.0.0.1:5000/

Questions/Suggestions/Bugfixes/Improvements/Contact:
----------------------------------------------------
	Twitter @etlow

License:
--------
	MIT License    

Notes:
------
	-When graph displayed left double click in a node will select it a target
	-When graph displayed right double click in a node will select it a source
	-Convert button will display the query required based on the shortest path calculated
	 if you want to interact directly with the selected target from the source.
	-Query button will send your specified query using the shortest path to the target
	-Query all button will send your specified query using the shortest path to all nodes
	- The test graph is just for modifiying D3 code in case you want to play with visualization.

	-Copy data.json file if you want to have a backup of the graph
	-Modify queries.json if you want to add your own queries
	-Check the terminal output to follow what Xolo is doing in the background
	-Be careful with the max recursion levels and the number of nodes , start low 
	 (maybe 2 - 3 levels and max 10 nodes per level)

	-This was an exercise for me to play and learn some D3 and the need to perform some db links visualizations. 
	 For that reason Xolo was made possible by learning and/or modifiying the code of the following individuals:
		
		DB links:
		
		-Antti Rantasaari <antti.rantasaari[at]netspi.com>',
          	'Scott Sutherland "nullbind" <scott.sutherland[at]netspi.com 
				https://blog.netspi.com/how-to-hack-database-links-in-sql-server/
				metasploit-framework/blob/master/modules/exploits/windows/mssql/mssql_linkcrawler.rb

		D3/Javascript/Flask:

		-Sumit Kumar 	https://github.com/reachsumit
		-Mike Bostock 	https://bl.ocks.org/mbostock
		-Simon Raper 	http://www.coppelia.io/2014/07/an-a-to-z-of-extra-features-for-the-d3-force-layout/


History
-------
	v1.0 Feb/2020 First release. Support for SQL server.











	



