#pragma once

#include <string>

#include "csv.hpp"

namespace mtcache {

struct TraceReq {
    uint64_t timeStamp;
    std::string key;
    uint32_t keySize;
    uint32_t valSize;
    uint64_t client;
    std::string operation;

    void printTraceReq();

    static TraceReq fromTwitterLine(csv::CSVRow&);
    static TraceReq fromFacebookLine(csv::CSVRow&);
};
} // namespace mtcache