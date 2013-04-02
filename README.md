# python-armet
> Clean and modern framework for creating RESTful APIs.

## Running the Tests
1. Open a shell and type in the proceeding commands.

2. Change into the **armet** root directory.

   ```sh
   cd /path/to/python-armet
   ```

3. Install **armet** in development mode with testing enabled.
   This will download all dependencies required for running the unit tests.

   ```sh
   pip install -e ".[test]"
   ```

4. Run the unit tests.

   ```sh
   nosetests
   ```

**Armet** is maintained with all tests passing at all times. If you find
a failure, please [report it](https://github.com/armet/python-armet/issues/new)
along with the version.
