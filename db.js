const moongose= require('moongose');
const DB_URL= (process.env.MONGO_URL) || 'mongodb://localhost/test'

const dbConnect= function() {
    const db= moongose.connection;
    db.on('error',console.error.bind(console, 'connection error: '));
    return mongoose.connect(DB_URL, { useNewUrlParser: true });

}

module.exports= dbConnect;