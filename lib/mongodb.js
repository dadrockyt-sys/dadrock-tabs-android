import { MongoClient } from 'mongodb';

const uri = process.env.MONGO_URL || 'mongodb://localhost:27017';
const dbName = process.env.DB_NAME || 'dadrock_tabs';

// Keep one MongoClient per warm serverless instance, but make sure a transient
// connection failure does not leave that instance holding a permanently
// rejected promise. MongoDB recommends reusing a MongoClient because it owns
// the connection pool; these timeouts simply fail a bad network handshake
// sooner so a fresh attempt can be made.
const clientOptions = {
  connectTimeoutMS: 10000,
  serverSelectionTimeoutMS: 15000,
  minPoolSize: 0,
  maxPoolSize: 20,
  retryReads: true,
  retryWrites: true,
};

function startClientConnection() {
  const client = new MongoClient(uri, clientOptions);

  let promise;
  promise = client.connect()
    .then((connectedClient) => {
      global._mongoClient = connectedClient;
      return connectedClient;
    })
    .catch(async (error) => {
      // A rejected cached promise can poison every request served by the same
      // warm function. Clear only the promise that actually failed so another
      // concurrent request can safely establish/reuse a fresh connection.
      if (global._mongoClientPromise === promise) {
        global._mongoClientPromise = null;
        global._mongoClient = null;
      }

      try {
        await client.close();
      } catch {
        // Ignore close errors from a client that never connected successfully.
      }

      throw error;
    });

  global._mongoClient = client;
  global._mongoClientPromise = promise;

  return promise;
}

function getClientPromise() {
  if (!global._mongoClientPromise) {
    return startClientConnection();
  }

  return global._mongoClientPromise;
}

export async function getDb() {
  const firstAttempt = getClientPromise();

  try {
    const client = await firstAttempt;
    return client.db(dbName);
  } catch {
    // startClientConnection() clears the failed cached promise. Retry once with
    // a fresh client so short-lived Atlas/TLS/network hiccups do not become a
    // persistent 5xx for every subsequent request on the same warm instance.
    const client = await getClientPromise();
    return client.db(dbName);
  }
}

// Backwards-compatible default export for any legacy importers.
const clientPromise = getClientPromise();
export default clientPromise;
