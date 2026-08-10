#!/bin/bash

# CA Firm MIS Backend - API Test Script
# This script tests all major API endpoints to verify functionality

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       CA Firm MIS Backend - API Test Suite                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

API_URL="http://localhost:8000"
PASS="✅"
FAIL="❌"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

# Function to run test
run_test() {
    test_count=$((test_count + 1))
    local test_name="$1"
    local endpoint="$2"
    local method="${3:-GET}"
    local data="$4"
    local expected_status="${5:-200}"
    
    echo -n "Test $test_count: $test_name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PATCH" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PATCH "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}${PASS} PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}${FAIL} FAIL (Expected $expected_status, got $status_code)${NC}"
        fail_count=$((fail_count + 1))
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SECTION 1: Basic Health Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Root endpoint" "/" "GET" "" 200
run_test "Health check" "/health" "GET" "" 200
run_test "API docs" "/docs" "GET" "" 200

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SECTION 2: Client Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "List all clients" "/clients" "GET" "" 200
run_test "Get single client" "/clients/1" "GET" "" 200
run_test "Get non-existent client" "/clients/999" "GET" "" 404
run_test "Create client" "/clients" "POST" '{
  "name": "Test API Client",
  "entity_type": "Company",
  "pan": "TESTAPI123",
  "partner_in_charge": "Test Partner"
}' 201

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SECTION 3: Task Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "List all tasks" "/tasks" "GET" "" 200
run_test "Get single task" "/tasks/1" "GET" "" 200
run_test "Get non-existent task" "/tasks/999" "GET" "" 404
run_test "Filter tasks by status" "/tasks?status=Awaiting%20Client" "GET" "" 200
run_test "Filter tasks by client" "/tasks?client_id=1" "GET" "" 200

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SECTION 4: Dashboard Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Tasks due this week" "/tasks/dashboard/due-this-week" "GET" "" 200
run_test "Overdue tasks" "/tasks/dashboard/overdue" "GET" "" 200
run_test "Tasks awaiting client" "/tasks/dashboard/awaiting-client" "GET" "" 200
run_test "Workload per assignee" "/tasks/dashboard/workload" "GET" "" 200

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SECTION 5: Document Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "List task documents" "/tasks/1/documents" "GET" "" 200
run_test "Create document" "/tasks/1/documents" "POST" '{
  "document_name": "Test Document",
  "is_received": false
}' 201

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SECTION 6: Validation Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "Create client with invalid data" "/clients" "POST" '{
  "name": "",
  "entity_type": "Company"
}' 422

run_test "Create task with invalid client" "/tasks" "POST" '{
  "client_id": 9999,
  "task_type": "GSTR-3B",
  "period_label": "Aug 2026",
  "due_date": "2026-09-20",
  "assignee": "Test",
  "status": "Not Started"
}' 404

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      TEST RESULTS                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Total Tests:  $test_count"
echo -e "Passed:       ${GREEN}$pass_count${NC}"
echo -e "Failed:       ${RED}$fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "System is working correctly and ready for use."
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please check the API logs for details:"
    echo "  docker compose logs api"
    exit 1
fi
