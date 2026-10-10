#!/usr/bin/env bash
# Run on macOS with OrbStack Docker CLI.
set -euo pipefail

# Fallback PATH for OrbStack Docker CLI if not in environment
if ! command -v docker >/dev/null 2>&1; then
  if [ -d "$HOME/.orbstack/bin" ]; then
    export PATH="$HOME/.orbstack/bin:$PATH"
  elif [ -d "/Applications/OrbStack.app/Contents/MacOS/xbin" ]; then
    export PATH="/Applications/OrbStack.app/Contents/MacOS/xbin:$PATH"
  fi
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/results"

CONTAINER_NAME="${CONTAINER_NAME:-codyssey-mysql}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-codyssey_2026_demo}"
HOST_PORT="${HOST_PORT:-3307}"

mkdir -p "$OUT_DIR"

# 1. Check Docker environment
if ! command -v docker >/dev/null 2>&1; then
  echo 'ERROR: Docker CLI not found. Start OrbStack.'
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo 'ERROR: Docker daemon unavailable.'
  exit 1
fi

# 2. Create or start MySQL
if ! docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
  echo "Creating MySQL container..."

  docker run -d \
    --name "$CONTAINER_NAME" \
    -e "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" \
    -p "127.0.0.1:${HOST_PORT}:3306" \
    -v codyssey_cafe_mysql_data:/var/lib/mysql \
    --restart unless-stopped \
    mysql:8.4 >/dev/null

elif [ "$(docker container inspect -f '{{.State.Running}}' "$CONTAINER_NAME")" != 'true' ]; then
  docker start "$CONTAINER_NAME" >/dev/null
fi

# 3. MySQL execution helper
mysql_exec() {
  docker exec -i \
    -e "MYSQL_PWD=$MYSQL_ROOT_PASSWORD" \
    "$CONTAINER_NAME" \
    mysql -uroot \
    --default-character-set=utf8mb4 \
    --table "$@"
}

# 4. Wait for MySQL
echo 'Waiting for MySQL...'
READY=0

for i in $(seq 1 90); do
  if printf 'SELECT 1;\n' | mysql_exec >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 2
done

if [ "$READY" -ne 1 ]; then
  echo "ERROR: MySQL connection failed."
  echo "Check: docker logs $CONTAINER_NAME"
  exit 1
fi

SCHEMA_FILE="$ROOT_DIR/01_schema.sql"
[ ! -f "$SCHEMA_FILE" ] && SCHEMA_FILE="$ROOT_DIR/schema.sql"

SEED_FILE="$ROOT_DIR/02_seed.sql"
[ ! -f "$SEED_FILE" ] && SEED_FILE="$ROOT_DIR/seed.sql"

QUERIES_FILE="$ROOT_DIR/03_queries.sql"
[ ! -f "$QUERIES_FILE" ] && QUERIES_FILE="$ROOT_DIR/queries.sql"

# 5. Create schema and insert sample data
# WARNING: Resets the codyssey_cafe database.
echo 'Creating database and tables...'

mysql_exec < "$SCHEMA_FILE" >/dev/null

echo 'Inserting sample data...'

mysql_exec < "$SEED_FILE" >/dev/null

# 6. Run Q01-Q15 and save results
echo 'Executing 15 SQL queries...'

for n in $(seq -w 1 15); do
  q="Q${n}"

  query="$(awk \
    -v begin="-- ${q}_START" \
    -v end="-- ${q}_END" '
      $0 == begin {inside=1; next}
      $0 == end {inside=0; exit}
      inside {print}
    ' "$QUERIES_FILE")"

  if [ -z "$query" ]; then
    echo "ERROR: Query $q not found."
    exit 1
  fi

  {
    echo "=== $q: MySQL 8.4 actual execution ==="
    echo 'SQL:'
    printf '%s\n' "$query"
    echo 'Result:'

    printf '%s\n' "$query" | mysql_exec codyssey_cafe

    case "$q" in
      Q13)
        echo 'Verification (after UPDATE):'

        printf \
          'SELECT order_id, status FROM orders WHERE order_id = 12;\n' \
          | mysql_exec codyssey_cafe
        ;;

      Q14)
        echo 'Verification (after DELETE):'

        printf \
          'SELECT COUNT(*) AS remaining_target FROM customer WHERE customer_id = 12;\nSELECT COUNT(*) AS remaining_customers FROM customer;\n' \
          | mysql_exec codyssey_cafe
        ;;

      Q15)
        echo 'Verification (after CREATE INDEX):'

        printf \
          "SHOW INDEX FROM orders WHERE Key_name = 'idx_orders_ordered_at';\n" \
          | mysql_exec codyssey_cafe
        ;;
    esac

  } > "$OUT_DIR/${q}.txt"

  echo "Saved: results/${q}.txt"
done

# 7. Validate evaluation requirements
echo 'Validating database...'

{
  echo '=== MySQL Evaluation Validation ==='

  echo '[Tables]'
  printf 'SHOW TABLES;\n' | mysql_exec codyssey_cafe

  echo '[Row counts]'
  printf "SELECT 'customer' AS table_name, COUNT(*) AS row_count FROM customer UNION ALL SELECT 'menu', COUNT(*) FROM menu UNION ALL SELECT 'orders', COUNT(*) FROM orders UNION ALL SELECT 'order_item', COUNT(*) FROM order_item;\n" \
    | mysql_exec codyssey_cafe

  echo '[Foreign key relationships]'
  printf "SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA='codyssey_cafe' AND REFERENCED_TABLE_NAME IS NOT NULL ORDER BY TABLE_NAME, COLUMN_NAME;\n" \
    | mysql_exec codyssey_cafe

  echo '[Invalid foreign key test]'

  if message="$(printf "INSERT INTO orders (order_id, customer_id, ordered_at, status) VALUES (9999, 99999, '2026-10-10 12:00:00', 'PAID');\n" \
      | mysql_exec codyssey_cafe 2>&1)"; then

    printf '%s\n' "$message"
    echo 'FAIL: Invalid customer ID was accepted!'
    exit 1

  else
    printf '%s\n' "$message"

    if [[ "$message" == *'ERROR 1452'* ]]; then
      echo 'PASS: FK rejected nonexistent customer_id (MySQL ERROR 1452).'
    else
      echo 'FAIL: INSERT failed for another reason.'
      exit 1
    fi
  fi

} > "$OUT_DIR/00_validation.txt"

# 8. Finish
echo
echo 'DONE: MySQL exercises completed.'
echo "Results saved to: $OUT_DIR"
echo 'Read README.md and STUDY_GUIDE.md.'
echo "Login: docker exec -it $CONTAINER_NAME mysql -uroot -p codyssey_cafe"
echo 'Demo password: codyssey_2026_demo (unless overridden).'
