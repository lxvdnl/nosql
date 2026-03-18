#!/bin/bash
set -e

wait_for_mongo() {
  local host=$1
  local port=$2
  until mongosh --host "$host" --port "$port" --eval "db.adminCommand({ ping: 1 })" >/dev/null 2>&1
  do
    sleep 2
  done
}

wait_for_mongo cfg1 27019
wait_for_mongo cfg2 27019
wait_for_mongo cfg3 27019
wait_for_mongo shard1 27018
wait_for_mongo shard2 27018
wait_for_mongo mongos 27017

mongosh --host cfg1 --port 27019 --eval '
try {
  rs.initiate({
    _id: "cfg-rs",
    configsvr: true,
    members: [
      { _id: 0, host: "cfg1:27019" },
      { _id: 1, host: "cfg2:27019" },
      { _id: 2, host: "cfg3:27019" }
    ]
  })
} catch (e) {
  print(e)
}
'

mongosh --host shard1 --port 27018 --eval '
try {
  rs.initiate({
    _id: "shard1-rs",
    members: [
      { _id: 0, host: "shard1:27018" }
    ]
  })
} catch (e) {
  print(e)
}
'

mongosh --host shard2 --port 27018 --eval '
try {
  rs.initiate({
    _id: "shard2-rs",
    members: [
      { _id: 0, host: "shard2:27018" }
    ]
  })
} catch (e) {
  print(e)
}
'

sleep 10

mongosh --host mongos --port 27017 --eval '
try { sh.addShard("shard1-rs/shard1:27018") } catch (e) { print(e) }
try { sh.addShard("shard2-rs/shard2:27018") } catch (e) { print(e) }
try { sh.enableSharding("university") } catch (e) { print(e) }

db = db.getSiblingDB("university")

try { db.createCollection("students") } catch (e) { print(e) }
try { db.students.createIndex({ student_id: "hashed" }) } catch (e) { print(e) }
try { sh.shardCollection("university.students", { student_id: "hashed" }) } catch (e) { print(e) }

try { db.createCollection("enrollments") } catch (e) { print(e) }
try { db.enrollments.createIndex({ student_id: "hashed" }) } catch (e) { print(e) }
try { sh.shardCollection("university.enrollments", { student_id: "hashed" }) } catch (e) { print(e) }

print("Cluster is ready")
'