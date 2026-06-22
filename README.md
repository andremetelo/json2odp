# json2odp
This is a simple GUI base Utility to quickly create an ODP Presentation from simple text-based content and jpg files.

The program is composed of two parts:
1 - A JSON parser that will generate the ODP file from an input file (sample file included).
2 - A GUI that will build the JSON files and generate the ODP directly from the GUI.

If you have an ODP with the template and background, both the GUI and the CLI can use the ODP as a base for the output ODP.

Code was created using Gemini, as I was testing its limit, and the ability to work on multiple files. That alone was worth the test. But I figured my daughters are getting the information on where their homework and projects are to be handled to their teachers as a PowerPoint / ODP file. I figured out that this will make their life easier. Hopefully, this will help somebody else as well.

Code is 100% python, and the only non-built-in requirement is python3-odp. I know, it probably would have been easier with odfdo, but I did not want to deal with virtual environments and install a new package. On top of that, remember that I was testing limits on Gemini (and boy, did the odf library cause it a lot of headaches to get the code to properly format fonts and backgrounds).

I am considering additional layouts, but for now, it handles slides as follows:
- Bullets in 1 column;
- Bullets in 2 columns;
- Bullets in 1 column + a graph;
- Full page Graph;
- Add speaker notes;

The JSON and code should be easy to add new tags for the columns, and then the annoying part is to modify the GUI to let you quickly input the content for the new layout.

