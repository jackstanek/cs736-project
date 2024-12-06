#include <iostream>
#include <sstream>
#include <stdexcept>

#include "csv.hpp"
#include "trace.hpp"

namespace mtcache {

/// Annotate exception with which field was being parsed
template <typename T> T get(csv::CSVField field, const std::string field_name) {
    try {
        return field.get<T>();
    } catch (std::runtime_error e) {
        std::stringstream ss;
        ss << field_name << ": " << e.what();
        throw std::runtime_error(ss.str());
    }
}

void TraceReq::printTraceReq() {
    std::cout << "(client: " << this->client << ") " << this->timeStamp << " : "
              << this->key << " : " << this->keySize << " : " << this->valSize
              << " : " << " : " << this->operation << " : " << std::endl;
}

TraceReq TraceReq::fromTwitterLine(csv::CSVRow& row) {
    return TraceReq(
        get<uint64_t>(row[0], "timeStamp"), get<std::string>(row[1], "key"),
        get<uint32_t>(row[2], "keySize"), get<uint32_t>(row[3], "valSize"),
        get<uint64_t>(row[4], "client"), get<std::string>(row[5], "operation"));
}

TraceReq TraceReq::fromFacebookLine(csv::CSVRow& row) {
    return TraceReq(
        get<uint64_t>(row[0], "timeStamp"), get<std::string>(row[1], "key"),
        get<uint32_t>(row[2], "keySize"), get<uint32_t>(row[5], "valSize"),
        get<uint64_t>(row[8], "client"), get<std::string>(row[3], "operation"));
}
} // namespace mtcache