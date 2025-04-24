import System.Environment (getArgs)

sumTwo :: Int -> Int -> Int
sumTwo x y = x + y

main :: IO ()
main = do
    args <- getArgs
    let a = read (args !! 0) :: Int
        b = read (args !! 1) :: Int
        result = sumTwo a b
    print result