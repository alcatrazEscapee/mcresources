# Benchmark Results

### File I/O Benchmark

This benchmark was developed to test different file I/O methods in order to both maximize performance and minimize unnecessary file writes. It can be ran with `python -m cProfile file_io_benchmark.py`. The file size, and the chance that the files would be identical were varied across three different methods.

- Trial 1: Small JSON (10 entries), Identical Data
- Trial 2: Large JSON (100 entries), Identical Data
- Trial 3: Small JSON (10 entries), Random Data
- Trial 4: Large JSON (100 entries), Random Data

All trials involved 10,000 file writes. Times are measured in seconds.

Trial | 1 | 2 | 3 | 4
--- | --- | --- | --- | ---
`always_overwrite` | 3.390 | 10.280 | 3.615 | 9.462
`overwrite_if_different` | 4.007 | 7.173 | 6.710 | 9.910
`overwrite_if_json_different` | 1.409 | 1.995 | 7.116 | 13.835

In situations where performance is important, the key factor is going to be a large number of mostly smaller files, with a small percentage needing modifications each run. In addition, avoiding unnecessary file writes is important for other reasons such as reducing load in IDE indexing. Thus, the `overwrite_if_json_different` was chosen to base `utils.write` on.
