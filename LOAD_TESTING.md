# Load Testing Guide for Localization Manager Backend

This guide explains how to run load tests against the Localization Manager Backend API using Locust.

## 🚀 Quick Start

### Prerequisites
- FastAPI server running on `http://localhost:8000`
- Locust installed (included in dev dependencies)

### Basic Load Test
```bash
# Start the FastAPI server first
uv run python main.py

# In another terminal, run a basic load test
python run_load_test.py
```

## 📊 Load Test Scenarios

### 1. **LocalizationManagerUser** (Default)
- **Purpose**: General API testing with realistic user behavior
- **Wait Time**: 1-3 seconds between requests
- **Tasks**:
  - Welcome component (high frequency - 4x weight)
  - Navigation component (medium frequency - 3x weight)
  - User profile component (medium frequency - 2x weight)
  - Footer component (medium frequency - 2x weight)
  - Health check (low frequency - 1x weight)

### 2. **CacheTestUser** (Cache Testing)
- **Purpose**: Test cache effectiveness
- **Wait Time**: 0.5-1.5 seconds between requests
- **Behavior**: Makes multiple requests to the same endpoints to test cache hits

### 3. **StressTestUser** (Stress Testing)
- **Purpose**: High-load stress testing
- **Wait Time**: 0.1-0.5 seconds between requests
- **Behavior**: Very fast, high-frequency requests

## 🎯 Test Commands

### Basic Load Test
```bash
# Default: 10 users, 2 users/sec spawn rate, 60 seconds
python run_load_test.py

# Custom parameters
python run_load_test.py --users 50 --spawn-rate 5 --run-time 120
```

### Interactive Web UI
```bash
# Start interactive test with web interface
python run_load_test.py --interactive

# Then open http://localhost:8089 in your browser
```

### Direct Locust Commands
```bash
# Headless test
uv run locust --host http://localhost:8000 --users 20 --spawn-rate 4 --run-time 2m --headless --only-summary

# Interactive test
uv run locust --host http://localhost:8000 --locustfile locustfile.py
```

## 📈 What Gets Tested

### API Endpoints
- `GET /api/component/{component_type}?lang={lang}` - Component localization
- `GET /health` - Health check

### Languages Tested
- English (`en`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)

### Components Tested
- Welcome component
- Navigation component
- User profile component
- Footer component

## 🔍 Cache Testing

The load test includes cache hit/miss tracking:

```python
# Cache hit detection
if data.get("cached", False):
    self.cache_hits += 1
else:
    self.cache_misses += 1
```

### Expected Cache Behavior
1. **First request**: Cache miss, component generated
2. **Subsequent requests**: Cache hit, served from cache
3. **After TTL expiration**: Cache miss, component regenerated

## 📊 Performance Metrics

### Key Metrics to Monitor
- **Response Time**: Average, median, 95th percentile
- **Requests/sec**: Throughput
- **Error Rate**: Percentage of failed requests
- **Cache Hit Rate**: Effectiveness of caching
- **Memory Usage**: Server resource consumption

### Expected Performance
- **Cached responses**: < 10ms
- **Uncached responses**: < 100ms
- **Error rate**: < 1%
- **Throughput**: > 1000 requests/sec (with caching)

## 🛠️ Advanced Configuration

### Custom Test Scenarios

#### High Load Test
```bash
python run_load_test.py --users 100 --spawn-rate 10 --run-time 300
```

#### Cache Effectiveness Test
```bash
# Run cache test user specifically
uv run locust --host http://localhost:8000 --users 5 --spawn-rate 1 --run-time 60 --headless --only-summary
```

#### Stress Test
```bash
# Run stress test user
uv run locust --host http://localhost:8000 --users 50 --spawn-rate 20 --run-time 120 --headless --only-summary
```

### Environment Variables
```bash
# Set custom host
export LOCUST_HOST=http://staging.example.com

# Set custom parameters
export LOCUST_USERS=50
export LOCUST_SPAWN_RATE=5
```

## 📋 Test Results Interpretation

### Good Performance Indicators
- Response times < 100ms for cached requests
- Response times < 500ms for uncached requests
- Error rate < 1%
- Cache hit rate > 80% after warm-up

### Performance Issues to Watch
- Response times > 1 second
- Error rate > 5%
- Memory usage growing continuously
- Cache hit rate < 50%

## 🔧 Troubleshooting

### Common Issues

#### Server Not Running
```bash
# Error: Connection refused
# Solution: Start the FastAPI server first
uv run python main.py
```

#### Locust Not Found
```bash
# Error: locust: command not found
# Solution: Install dev dependencies
uv sync --extra dev
```

#### Port Already in Use
```bash
# Error: Address already in use
# Solution: Change port or kill existing process
uv run locust --port 8090
```

### Debug Mode
```bash
# Run with verbose output
uv run locust --host http://localhost:8000 --users 1 --spawn-rate 1 --run-time 10 --headless --loglevel DEBUG
```

## 📝 Example Test Results

```
Name                                                          # reqs      # fails  |     Avg     Min     Max  |  Median   req/s  failures/s
--------------------------------------------------------------------------------------------------------------------------------------------
GET /api/component/welcome                                     1,234          0  |     45     12    156  |      38   20.57         0.00
GET /api/component/navigation                                    823          0  |     38     10    134  |      32   13.72         0.00
GET /api/component/user_profile                                  456          0  |     42     15    178  |      35    7.60         0.00
GET /api/component/footer                                        345          0  |     40     12    145  |      33    5.75         0.00
GET /health                                                      123          0  |     12      5     45  |      10    2.05         0.00
--------------------------------------------------------------------------------------------------------------------------------------------
Aggregated                                                     2,981          0  |     41     10    178  |      34   49.68         0.00

Response time percentiles (approximated)
Type     Name                                                              50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|------------------------------------------------------------|---------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
GET      /api/component/welcome                                           38     45     52     58     78     95    120    140    150    156    156   1234
GET      /api/component/navigation                                        32     38     45     52     68     85    110    125    130    134    134    823
GET      /api/component/user_profile                                      35     42     48     55     75     92    115    135    150    170    178    456
GET      /api/component/footer                                            33     40     45     52     68     85    110    125    130    140    145    345
GET      /health                                                          10     12     15     18     25     32     40     45     45     45     45    123
--------|------------------------------------------------------------|---------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
None     Aggregated                                                       34     41     47     54     74     91    115    135    150    170    178   2981
```

## 🎯 Best Practices

1. **Start Small**: Begin with low user counts and gradually increase
2. **Monitor Resources**: Watch CPU, memory, and network usage
3. **Test Cache Behavior**: Verify cache hits improve performance
4. **Use Realistic Data**: Test with actual language combinations
5. **Monitor Error Rates**: Keep error rates below 1%
6. **Test Different Scenarios**: Mix cached and uncached requests
7. **Document Results**: Keep track of performance improvements

## 📚 Additional Resources

- [Locust Documentation](https://docs.locust.io/)
- [FastAPI Performance](https://fastapi.tiangolo.com/tutorial/performance/)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/) 