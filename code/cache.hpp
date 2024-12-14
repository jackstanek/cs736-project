#pragma once

#include <algorithm>
#include <cstdint>
#include <memory>
#include <optional>

#include <gcache/ghost_kv_cache.h>
#include <gcache/stat.h>
#include <vector>

#include "trace.hpp"

namespace mtcache {

template <typename Cache> class TenantCache {
  private:
    std::unique_ptr<Cache> cache;
    uint32_t reqs_processed;
    std::optional<uint64_t> first_ts;
    std::optional<uint64_t> last_ts;

  public:
    TenantCache<Cache>(uint32_t tick, uint32_t min_count, uint32_t max_count)
        : cache(std::make_unique<Cache>(tick, min_count, max_count)) {}

    void access(const TraceReq& req) {
        cache->access(req.key, req.keySize + req.valSize);
        if (last_ts) {
            last_ts = std::max(req.timeStamp, *last_ts);
        } else {
            first_ts = req.timeStamp;
            last_ts = req.timeStamp;
        }
        reqs_processed++;
    }

    const std::vector<std::tuple<
        /*count*/ uint32_t, /*size*/ uint32_t, /*miss_rate*/ gcache::CacheStat>>
    get_cache_stat_curve() {
        return cache->get_cache_stat_curve();
    }
};

} // namespace mtcache