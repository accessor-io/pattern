use std::io::Read;

let mut bytes = s.bytes().filter_map(|r| r.ok()); 