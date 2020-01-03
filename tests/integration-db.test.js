const Puntos= require('../app/app.py')
const mongoose= require('mongoose');
const dbConnect= require('../db');

describe('Puntos DB connection', () => {
        beforeAll(() => {
            return dbConnect();

        })

        beforeEach((done) => {
            Puntos.deleteMany({}, (err) => {
                done();

            });

        });

        it('writes a contact in the DB', (done) => {
            const puntos= new Puntos({dni:'30214587S'});
                expect(err).toBeNull();
                Puntos.find({}, (err,contacts)=> {
                    expect(puntos).toBeArrayOfSize(1);
                    done();

                });

            });
})


        afterAll((done) => {
            mongoose.connection.db.dropDatabase(() => {
                mongoose.connection.close(done);
            });
        });
