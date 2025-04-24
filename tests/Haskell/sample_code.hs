import System.Environment (getArgs)

sumTwo :: Int -> Int -> Int
sumTwo x y = x + y

main :: IO ()
main = do
    args <- getArgs
    let x = read (args !! 0) :: Int
        y = read (args !! 1) :: Int
        result = sumTwo x y
    print result