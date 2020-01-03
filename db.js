const moongose= require('moongose');
const DB_URL= (process.env.MONGO_URL) || 'mongodb+srv://api:QzEbuGslcPlAy7KN@api-info-puntos-dgt-tp10l.mongodb.net/test?retryWrites=true&w=majority'

const dbConnect= function() {
    const db= moongose.connection;
    db.on('error',console.error.bind(console, 'connection error: '));
    return mongoose.connect(DB_URL, { useNewUrlParser: true });

}

module.exports= dbConnect;