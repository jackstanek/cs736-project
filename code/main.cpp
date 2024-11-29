#include <cstdint>
#include <csv.hpp>
#include <fstream>
#include <gcache/ghost_kv_cache.h>
#include <iostream>
#include <ostream>
#include <string>

struct TraceReq {
    int timeStamp;
    std::string key;
    int keySize;
    int valSize;
    int client;
    std::string operation;

    static TraceReq fromRow(const csv::CSVRow& row) {
        return TraceReq(row[0].get<int>(), row[1].get<std::string>(),
                        row[2].get<int>(), row[3].get<int>(), row[4].get<int>(),
                        row[5].get<std::string>());
    };

    void printTraceReq() const {
        std::cout << this->timeStamp << " : " << this->key << " : "
                  << this->keySize << " : " << this->valSize << " : "
                  << this->client << " : " << this->operation << " : "
                  << std::endl;
    }
};

void writeMRCOutput(
    const std::vector<std::tuple<uint32_t, uint32_t, gcache::CacheStat>>&
        curve) {
    for (auto& point : curve) {
        std::cout << std::get<0>(point) << " " << std::get<1>(point)
                  << std::get<2>(point) << std::endl;
    }
}

void usage(const std::string& execName) {
    std::cout << "usage: " << execName << " <trace>" << std::endl;
    exit(1);
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        usage(argv[0]);
    }
    std::string tracePath(argv[1]);
    std::ifstream file(tracePath);

    csv::CSVReader reader(file);

    gcache::SampledGhostKvCache<5> ghost(1024 * 64, 1024 * 64, 1024 * 1024);

    for (csv::CSVRow& row : reader) {
        if (row[0].is_int() && row[2].is_int() && row[3].is_int() &&
            row[4].is_int()) {
            auto req = TraceReq::fromRow(row);
            ghost.access(req.key, req.keySize + req.valSize);
        }
    }

    file.close();

    auto curve = ghost.get_cache_stat_curve();

    writeMRCOutput(curve);

    return 0;
}