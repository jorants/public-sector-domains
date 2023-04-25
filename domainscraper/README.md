# File overview

| File                             | Purpose                                                                                                                                                              |
| [__init__.py](__init__.py)       | Empty at the moment, should eventually contain exported interface for running as a library                                                                           |
| [__main__.py](__main__.py)       | Contians the code for the CLI interface. Can be run directly using `python -m domainscraper`, but is also exposed through the `domainscraper` command when installed |
| [base.py](base.py)               | Code that deals with finding and running getters                                                                                                                     |
| [common.py](common.py)           | Common datatype definitions                                                                                                                                          |
| [db.py](db.py)                   | Database interface and models. Contains the logic to search in past results as well as update with new results.                                                      |
| [getterutils.py](getterutils.py) | Everything that a getter file might need to import. Mostly helper functions and some common datatypes.                                                               |
| [getters/](getters/)             | Folder that houses al of the actual scraping scripts ("getters").                                                                                                    |
| [output.py](output.py)           | Functions to export to various formats form the database.                                                                                                            |
